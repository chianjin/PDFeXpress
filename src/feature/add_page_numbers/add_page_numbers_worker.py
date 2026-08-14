"""Add page numbers to a single PDF (runs in a subprocess so the UI stays responsive)."""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo
from typing import Any

import pymupdf

from core.progress_dialog import ProgressDialog
from util.i18n import gettext_text as _
from util.page_number_rule import build_page_number_map

CM_TO_PT = 72.0 / 2.54

# Built-in base-14 fonts that PyMuPDF renders without external files.
FONT_BASE = {
    'Courier': {'regular': 'cour', 'bold': 'cobo'},
    'Times': {'regular': 'tiro', 'bold': 'tibo'},
    'Helvetica': {'regular': 'helv', 'bold': 'hebo'},
}

# insert_textbox horizontal alignment.
LEFT, CENTER, RIGHT = 0, 1, 2


def _geometry(
    page,
    vertical,
    horizontal,
    page_index,
    top_cm,
    bottom_cm,
    left_cm,
    right_cm,
    mirror_cm,
    font_size,
):
    """Return (Rect, align) for the page-number box.

    PyMuPDF Page coords: top-left origin, y grows downward, so the header sits
    near the top (small y) and the footer near the bottom (large y).
    """
    w, h = page.rect.width, page.rect.height
    band = float(font_size) * 2.0

    if vertical == 'header':
        y0 = top_cm * CM_TO_PT
    else:
        y0 = h - bottom_cm * CM_TO_PT - band
    y1 = y0 + band

    if horizontal == 'left':
        x0, x1, align = left_cm * CM_TO_PT, w, LEFT
    elif horizontal == 'right':
        x0, x1, align = 0.0, w - right_cm * CM_TO_PT, RIGHT
    elif horizontal == 'outside':
        m = mirror_cm * CM_TO_PT
        x0, x1, align = (0.0, w - m, RIGHT) if page_index % 2 == 1 else (m, w, LEFT)
    elif horizontal == 'inside':
        m = mirror_cm * CM_TO_PT
        x0, x1, align = (m, w, LEFT) if page_index % 2 == 1 else (0.0, w - m, RIGHT)
    else:  # center
        x0, x1, align = 0.0, w, CENTER

    return pymupdf.Rect(x0, y0, x1, y1), align


def worker(params: dict[str, Any], progress_queue: Queue, cancel_event: Event) -> None:
    options = params['options']
    try:
        doc = pymupdf.open(str(Path(params['inputs'][0])))
        total = doc.page_count
        page_map = build_page_number_map(options['rule'], total)
        base_font = FONT_BASE[options['font_family']][
            'bold' if options['font_bold'] else 'regular'
        ]
        fs = options['font_size']

        cancelled = False
        for index in range(1, total + 1):
            if cancel_event.is_set():
                cancelled = True
                break
            progress_queue.put(
                (
                    'progress',
                    index,
                    total,
                    f'{_("Adding page numbers...")} {index}/{total}',
                )
            )
            if index not in page_map:
                continue
            page = doc[index - 1]
            rect, align = _geometry(
                page,
                options['vertical'],
                options['horizontal'],
                index,
                options['top_margin_cm'],
                options['bottom_margin_cm'],
                options['left_margin_cm'],
                options['right_margin_cm'],
                options['mirror_margin_cm'],
                fs,
            )
            page.insert_textbox(
                rect, page_map[index], fontname=base_font, fontsize=fs, align=align
            )

        if cancelled:
            doc.close()
            progress_queue.put(('cancelled', None))
            return

        Path(params['output']).parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(params['output']))
        doc.close()
        progress_queue.put(('done', str(params['output'])))
    except Exception as exc:
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


def run_add_page_numbers_with_progress(master, params: dict[str, Any]) -> None:

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    finished = False

    def _finish():
        nonlocal finished
        if finished:
            return
        finished = True
        if process is not None and process.is_alive():
            process.join(timeout=2)
        dialog.destroy()

    def _on_cancel():
        cancel_event.set()
        if process is not None and process.is_alive():
            process.terminate()
        _finish()

    dialog = ProgressDialog(
        master,
        title=_('Add Page Numbers'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    def _poll():
        if finished:
            return
        try:
            while True:
                msg = progress_queue.get_nowait()
                kind = msg[0]
                if kind == 'progress':
                    _, cur, tot, text = msg
                    dialog.set_progress((cur / tot) if tot else 0, text)
                elif kind == 'done':
                    _finish()
                    showinfo(title=_('Done'), message=_('Page Numbers Added'))
                    return
                elif kind == 'error':
                    _finish()
                    showerror(title=_('Error'), message=msg[1])
                    return
                elif kind == 'cancelled':
                    _finish()
                    return
        except Empty:
            pass
        if not finished:
            master.after(100, _poll)

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
