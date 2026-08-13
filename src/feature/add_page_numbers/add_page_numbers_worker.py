"""Add page numbers to a single PDF.

The heavy work runs in a separate process so the UI stays responsive. Progress is
reported back through a ``multiprocessing.Queue`` and shown via
``core.progress_dialog.ProgressDialog`` (see ``run_add_page_numbers_with_progress``).

Drawing uses ``Page.insert_textbox`` with the built-in base-14 fonts. This PyMuPDF
build only ships some oblique outlines, so italic / bold-italic are rendered by
shearing the regular / bold glyphs with a morph matrix instead of a missing font.
"""

import pymupdf
from multiprocessing import Process, Queue, Event
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo
from typing import Any, Dict, Tuple

from util.i18n import gettext_text as _
from util.page_number_rule import build_page_number_map

# 1 cm == 72 / 2.54 points.
CM_TO_PT = 72.0 / 2.54

# Built-in base-14 font abbreviations that this PyMuPDF build can render.
FONT_BASE = {
    'Courier': {'regular': 'cour', 'bold': 'cobo'},
    'Times': {'regular': 'tiro', 'bold': 'tibo'},
    'Helvetica': {'regular': 'helv', 'bold': 'hebo'},
}

# Italic variants are synthesized by shearing the regular / bold glyphs.
STYLE_ITALIC = {
    'Regular': False,
    'Bold': False,
    'Italic': True,
    'Bold Italic': True,
}
STYLE_BOLD = {
    'Regular': False,
    'Bold': True,
    'Italic': False,
    'Bold Italic': True,
}

# Horizontal alignment for insert_textbox (0 left, 1 center, 2 right).
ALIGN = {'left': 0, 'center': 1, 'right': 2}

# Shear matrix that fakes an italic slant (higher y leans right).
ITALIC_SKEW = pymupdf.Matrix(1, 0, 0.25, 1, 0, 0)


def _geometry(page, vertical, horizontal, page_index, top_cm, bottom_cm,
              left_cm, right_cm, mirror_cm, font_size):
    """Return ``(Rect, align)`` for the page-number text box on one page."""
    width = page.rect.width
    height = page.rect.height
    fs = float(font_size)
    # insert_textbox anchors the text baseline at rect.y0 and draws upward
    # (page y grows upward), so the rect must be tall enough for one line.
    band_h = fs * 2.0
    if vertical == 'header':
        # text top sits one font size below the top edge minus the margin
        y0 = height - top_cm * CM_TO_PT - fs
    else:  # footer
        y0 = bottom_cm * CM_TO_PT
    y1 = y0 + band_h

    if horizontal in ('left', 'center', 'right'):
        if horizontal == 'left':
            x0 = left_cm * CM_TO_PT
            x1 = width
            align = ALIGN['left']
        elif horizontal == 'right':
            x0 = 0.0
            x1 = width - right_cm * CM_TO_PT
            align = ALIGN['right']
        else:  # center
            x0 = 0.0
            x1 = width
            align = ALIGN['center']
    else:
        margin = mirror_cm * CM_TO_PT
        odd = (page_index % 2 == 1)
        # Outside = away from the binding; inside = toward it (Chinese LTR book).
        if horizontal == 'outside':
            if odd:  # odd page is the right-hand page -> outside = right
                x0, x1, align = 0.0, width - margin, ALIGN['right']
            else:
                x0, x1, align = margin, width, ALIGN['left']
        else:  # inside
            if odd:
                x0, x1, align = margin, width, ALIGN['left']
            else:
                x0, x1, align = 0.0, width - margin, ALIGN['right']

    return pymupdf.Rect(x0, y0, x1, y1), align


def worker(params: Dict[str, Any], progress_queue: Queue, cancel_event: Event) -> None:
    """Draw page numbers onto a single input PDF and report progress.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_path)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params.get('inputs', [])
    output = params.get('output')
    options = params.get('options', {})

    rule = options.get('rule', '')
    font_family = options.get('font_family', 'Helvetica')
    font_style = options.get('font_style', 'Regular')
    font_size = int(options.get('font_size', 10))
    vertical = options.get('vertical', 'footer')
    horizontal = options.get('horizontal', 'center')
    top_cm = float(options.get('top_margin_cm', 1.0))
    bottom_cm = float(options.get('bottom_margin_cm', 1.0))
    left_cm = float(options.get('left_margin_cm', 1.0))
    right_cm = float(options.get('right_margin_cm', 1.0))
    mirror_cm = float(options.get('mirror_margin_cm', 1.0))

    try:
        if not inputs:
            progress_queue.put(('error', _('No input files.')))
            return

        src_path = Path(inputs[0])
        doc = pymupdf.open(str(src_path))
        total = doc.page_count
        page_map = build_page_number_map(rule, total)

        use_bold = STYLE_BOLD.get(font_style, False)
        family_fonts = FONT_BASE.get(font_family, FONT_BASE['Helvetica'])
        base_font = family_fonts['bold' if use_bold else 'regular']
        italic = STYLE_ITALIC.get(font_style, False)

        for index in range(1, total + 1):
            if cancel_event.is_set():
                doc.close()
                progress_queue.put(('cancelled', None))
                return
            progress_queue.put(
                ('progress', index, total,
                 f'{_("Adding page numbers...")} {index}/{total}')
            )
            if index not in page_map:
                continue  # pages outside the rule carry no number
            text = page_map[index]
            page = doc[index - 1]
            rect, align = _geometry(
                page, vertical, horizontal, index,
                top_cm, bottom_cm, left_cm, right_cm, mirror_cm, font_size,
            )
            draw_kwargs = dict(fontname=base_font, fontsize=font_size, align=align)
            if italic:
                draw_kwargs['morph'] = (pymupdf.Point(rect.x0, rect.y0), ITALIC_SKEW)
            page.insert_textbox(rect, text, **draw_kwargs)
            if cancel_event.is_set():
                doc.close()
                progress_queue.put(('cancelled', None))
                return

        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        progress_queue.put(('progress', total, total, _('Saving...')))
        doc.save(str(out_path))
        doc.close()
        progress_queue.put(('done', str(out_path)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


def run_add_page_numbers_with_progress(master, params: Dict[str, Any]) -> None:
    """Run page numbering in a subprocess and show progress via ProgressDialog."""
    from core.progress_dialog import ProgressDialog

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    state = {'finished': False}

    dialog = ProgressDialog(
        master,
        title=_('Add Page Numbers'),
        label_text=_('Preparing...'),
        cancel_command=lambda: _on_cancel(),
        mode='determinate',
    )

    def _finish():
        if state['finished']:
            return
        state['finished'] = True
        if process is not None and process.is_alive():
            process.join(timeout=2)
        dialog.destroy()

    def _on_cancel():
        cancel_event.set()
        if process is not None and process.is_alive():
            process.terminate()
        _finish()

    def _poll():
        if state['finished']:
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
                    showinfo(
                        title=_('Done'),
                        message=_('Page Numbers Added'),
                    )
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

        if not state['finished']:
            master.after(100, _poll)

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
