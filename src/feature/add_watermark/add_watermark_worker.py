"""Add watermark worker.

Multi-input PDF -> output folder, one ``{stem}.{_('Watermark')}.pdf`` per input.

Text watermark: a tiled, 36-degree skewed diagonal pattern drawn on the **top**
layer (overlay=True) with black fill + low fill_opacity so it stays legible on
both light and dark content. CJK text uses the built-in ``china-s`` font;
western text uses base-14 ``Times-Roman``.

Progress is counted per page (denominator = total pages across all inputs).
A single failed file is skipped and listed in the final summary.
"""

import math
from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showwarning
from typing import Any

import pymupdf

from core.progress_dialog import ProgressDialog
from util.helpers import prompt_open_output
from util.i18n import gettext_text as _

DEFAULT_FONT_SIZE = 36
# Pure black + low fill_opacity: shows up as a faint gray on white pages and
# stays visible on darker content; tune WATERMARK_FILL_OPACITY to taste.
WATERMARK_TEXT_COLOR = (0.0, 0.0, 0.0)
WATERMARK_FILL_OPACITY = 0.15
MARGIN_CM = 2.0
MARGIN_PT = MARGIN_CM * 72.0 / 2.54
TILT_DEGREES = 36


def _choose_font(text: str) -> str:
    """Built-in fonts only: CJK -> china-s, otherwise Times-Roman."""
    if any('\u4e00' <= ch <= '\u9fff' for ch in text):
        return 'china-s'
    return 'Times-Roman'


def _draw_text_watermark(page, text: str, font_size: int) -> None:
    """Tile ``text`` across the page as a 36-degree skewed diagonal pattern.

    Uses ``insert_text`` (not ``insert_textbox``) so the text is always drawn
    even when the measured width is large (e.g. mixed CJK+Latin under the
    ``china-s`` font, which renders Latin full-width) — ``insert_textbox`` would
    silently refuse on overflow. Drawn on the top layer with a low fill_opacity
    so the underlying content (including text backgrounds) remains readable.
    """
    fontname = _choose_font(text)
    text_w = pymupdf.get_text_length(text, fontname=fontname, fontsize=font_size)
    rad = math.radians(TILT_DEGREES)
    cos_r, sin_r = math.cos(rad), math.sin(rad)
    rot = pymupdf.Matrix(cos_r, -sin_r, sin_r, cos_r, 0.0, 0.0)

    area = pymupdf.Rect(
        MARGIN_PT,
        MARGIN_PT,
        page.rect.width - MARGIN_PT,
        page.rect.height - MARGIN_PT,
    )

    cell_w = text_w + font_size * 2.0
    cell_h = font_size * 3.0

    x_start = area.x0 - cell_w
    x_end = area.x1 + cell_w
    y_start = area.y0 - cell_h
    y_end = area.y1 + cell_h

    y = y_start
    while y < y_end:
        x = x_start
        while x < x_end:
            cx = x + cell_w / 2.0
            cy = y + cell_h / 2.0
            page.insert_text(
                (cx - text_w / 2.0, cy),
                text,
                fontname=fontname,
                fontsize=font_size,
                color=WATERMARK_TEXT_COLOR,
                fill_opacity=WATERMARK_FILL_OPACITY,
                overlay=True,
                morph=(pymupdf.Point(cx, cy), rot),
            )
            x += cell_w
        y += cell_h


def worker(params: dict[str, Any], progress_queue: Queue, cancel_event) -> None:
    """Add a text watermark to every input PDF and write results into the folder.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_folder)
        ('partial', output_folder, success_count, failed_count, summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    text = options['text']

    try:
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Pre-count total pages for the progress denominator.
        total_pages = 0
        for in_path in inputs:
            with pymupdf.open(in_path) as doc:
                total_pages += doc.page_count

        page_index = 0
        failed: list[tuple[str, str]] = []
        success_count = 0

        for in_path in inputs:
            src = Path(in_path)
            try:
                with pymupdf.open(src) as doc:
                    for p_idx in range(doc.page_count):
                        if cancel_event.is_set():
                            progress_queue.put(('cancelled', None))
                            return
                        page_index += 1
                        progress_queue.put(
                            (
                                'progress',
                                page_index - 1,
                                total_pages,
                                f'{_("Watermarking...")} {page_index}/{total_pages}',
                            )
                        )
                        page = doc[p_idx]
                        _draw_text_watermark(page, text, DEFAULT_FONT_SIZE)
                    out_file = out_dir / f'{src.stem}.{_("Watermark")}.pdf'
                    doc.save(out_file)
                    success_count += 1
            except Exception as exc:
                failed.append((src.name, f'{type(exc).__name__}: {exc}'))

        progress_queue.put(('progress', total_pages, total_pages, _('Done')))
        if failed:
            summary = _('{} file(s) failed:').format(len(failed))
            for name, message in failed:
                summary += f'\n- {name}: {message}'
            progress_queue.put(
                ('partial', str(out_dir), success_count, len(failed), summary)
            )
        else:
            progress_queue.put(('done', str(out_dir)))

    except Exception as exc:
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


def run_add_watermark_with_progress(master, params: dict[str, Any]) -> None:
    """Run watermarking in a subprocess and show progress via ProgressDialog."""

    progress_queue: Queue = Queue()
    cancel_event = Event()
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
        title=_('Add Watermark'),
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
                    current, total, text = msg[1], msg[2], msg[3]
                    fraction = (current / total) if total else 0
                    dialog.set_progress(fraction, text)
                elif kind == 'done':
                    _finish()
                    prompt_open_output(master, params['output'])
                    return
                elif kind == 'partial':
                    _out_dir, _ok, _fail, summary = msg[1], msg[2], msg[3], msg[4]
                    _finish()
                    showwarning(title=_('Done with errors'), message=summary)
                    return
                elif kind == 'error':
                    err = msg[1]
                    _finish()
                    showerror(title=_('Error'), message=err)
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
