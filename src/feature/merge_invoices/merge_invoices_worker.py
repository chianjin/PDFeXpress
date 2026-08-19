"""Merge invoices worker.

Invoices are auto-classified, then stitched onto A4 pages:

* **Regular invoice** -- a single page whose height is <= 15 cm. Two of them
  are stacked top/bottom onto one A4 page (slots of 14 cm each, leaving a
  small bottom margin).
* **Other invoice** -- multi-page, or a single page taller than 15 cm. Every
  source page is placed onto its own A4 page, top-left aligned (the original
  top margin is preserved) and only scaled down when it would exceed the A4
  bounds.

The two result sets are concatenated (regular pages first, then other pages)
into a single output PDF.

The heavy work runs in a separate process so the UI stays responsive; progress
is reported through a ``multiprocessing.Queue`` and shown via
``core.progress_dialog.ProgressDialog`` (see ``run_merge_invoices_with_progress``).
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror

import pymupdf

from core.progress_dialog import ProgressDialog
from util.helpers import prompt_open_output
from util.i18n import gettext_text as _

# ---------------------------------------------------------------------------
# Geometry constants (PyMuPDF works in points: 1 cm = 28.3464567 pt).
# ---------------------------------------------------------------------------
CM = 28.3464567
A4_W, A4_H = pymupdf.paper_size('a4')  # (595, 842)
REGULAR_SLOT_H = 14 * CM  # 14 cm slot for the 2-up layout
REGULAR_MAX_H = 15 * CM  # classification threshold (relaxed)


def classify(doc: 'pymupdf.Document') -> str:
    """Return 'regular' or 'other' for a (baked) invoice document."""
    if doc.page_count > 1:
        return 'other'
    return 'regular' if doc[0].rect.height <= REGULAR_MAX_H else 'other'


def _place_regular(
    out: 'pymupdf.Document', docs: list['pymupdf.Document'], refs: list[tuple[int, int]]
) -> None:
    """Place regular invoice pages two-up (top/bottom) onto A4 pages."""
    for i in range(0, len(refs), 2):
        page = out.new_page(width=A4_W, height=A4_H)
        d0, p0 = refs[i]
        page.show_pdf_page(
            pymupdf.Rect(0, 0, A4_W, REGULAR_SLOT_H),
            docs[d0],
            p0,
            keep_proportion=True,
        )
        if i + 1 < len(refs):
            d1, p1 = refs[i + 1]
            page.show_pdf_page(
                pymupdf.Rect(0, REGULAR_SLOT_H, A4_W, 2 * REGULAR_SLOT_H),
                docs[d1],
                p1,
                keep_proportion=True,
            )


def _place_other(
    out: 'pymupdf.Document', docs: list['pymupdf.Document'], refs: list[tuple[int, int]]
) -> None:
    """Place other invoice pages one-per-A4, top-left aligned, fit-to-A4."""
    for d_idx, pno in refs:
        src = docs[d_idx]
        w = src[pno].rect.width
        h = src[pno].rect.height
        scale = min(1.0, A4_W / w, A4_H / h)
        rect = pymupdf.Rect(0, 0, w * scale, h * scale)
        page = out.new_page(width=A4_W, height=A4_H)
        page.show_pdf_page(rect, src, pno, keep_proportion=True)


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict, progress_queue: Queue, cancel_event) -> None:
    """Classify and merge invoice PDFs into one output PDF, report progress.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_path)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']

    try:
        total = len(inputs)
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        opened: list[pymupdf.Document] = []  # baked source docs, kept open
        regular: list[tuple[int, int]] = []  # (doc_index, page_index)
        other: list[tuple[int, int]] = []

        for index, in_path in enumerate(inputs, start=1):
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            src_path = Path(in_path)
            progress_queue.put(('progress', index - 1, total, f'{_("Merging...")} {index}/{total}'))

            src = pymupdf.open(src_path)
            src.bake()  # flatten form fields / annotations in place
            di = len(opened)
            opened.append(src)
            kind = classify(src)
            bucket = regular if kind == 'regular' else other
            for pno in range(src.page_count):
                bucket.append((di, pno))

        with pymupdf.open() as out:
            _place_regular(out, opened, regular)
            _place_other(out, opened, other)

            progress_queue.put(('progress', total, total, _('Saving...')))
            progress_queue.put(('progress', total, total, _('Done')))
            out.save(output_path)
        for d in opened:
            d.close()

        progress_queue.put(('done', str(output_path)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_merge_invoices_with_progress(master, params: dict) -> None:
    """Run the invoice merge in a subprocess and show progress."""

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
        title=_('Merge Invoices'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    def _poll():
        nonlocal finished
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
