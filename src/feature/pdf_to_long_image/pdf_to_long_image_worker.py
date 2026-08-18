"""PDF to Long Image worker.

Single input PDF -> single long JPEG. Selected pages (1-based range expression
``n`` / ``n-m`` / empty = all) are rendered at a fixed 150 DPI, scaled to a
common width, and concatenated vertically into one image without external
dependencies (pure PyMuPDF byte assembly). If the resulting height exceeds the
JPEG limit (65500 px) the job stops with an error instead of scaling down.
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror
from util.helpers import prompt_open_output

import pymupdf

from core.progress_dialog import ProgressDialog
from util.i18n import gettext_text as _

# Fixed internal rendering settings (UI-immutable).
DPI = 150
QUALITY = 80
# MuPDF hard limit on a single JPEG dimension.
MAX_PIXEL = 65500


def _parse_range(rng: str, total: int) -> list[int]:
    """Return 0-based page indices for a 1-based range expression.

    ``''`` -> all pages; ``'n'`` -> single page; ``'n-m'`` -> inclusive range.
    Raises ``ValueError`` with a localized message on malformed/out-of-range input.
    """
    rng = (rng or '').strip()
    if rng == '':
        return list(range(total))

    if '-' in rng:
        left, right = rng.split('-', 1)
        start = int(left)
        end = int(right)
    else:
        start = end = int(rng)

    if start < 1 or end < 1 or start > total or end > total:
        raise ValueError(_('Page number out of range (1-{}).').format(total))
    if start > end:
        raise ValueError(_('Start page cannot be greater than end page.'))

    return list(range(start - 1, end))


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict, progress_queue: Queue, cancel_event: Event) -> None:
    """Render selected pages of a PDF into one long JPEG.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    rng = options['range']

    try:
        if len(inputs) != 1:
            progress_queue.put(('error', _('Exactly one input PDF is required.')))
            return

        src = Path(inputs[0])
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with pymupdf.open(src) as doc:
            total = doc.page_count
            if total == 0:
                progress_queue.put(('error', _('The PDF has no pages.')))
                return

            try:
                pages = _parse_range(rng, total)
            except ValueError as ve:
                progress_queue.put(('error', str(ve)))
                return
            if not pages:
                progress_queue.put(('error', _('No pages selected.')))
                return

            # Common target width = widest page rendered at the fixed DPI.
            progress_queue.put(('progress', 1, 3, f'{_("Converting...")}'))
            max_rect_w = max(doc[p].rect.width for p in pages)
            target_width = round(max_rect_w * DPI / 72.0)

            samples: list[bytes] = []
            total_height = 0
            for i, p in enumerate(pages, start=1):
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return
                progress_queue.put(
                    (
                        'progress',
                        i,
                        1 + len(pages),
                        f'{_("Converting...")} {i}/{len(pages)}',
                    )
                )
                page = doc[p]
                scale = target_width / page.rect.width
                matrix = pymupdf.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                samples.append(pix.samples)
                total_height += pix.height

            if total_height > MAX_PIXEL:
                progress_queue.put(
                    (
                        'error',
                        _(
                            'Resulting image height {} px exceeds the JPEG limit of {} px.'
                        ).format(total_height, MAX_PIXEL),
                    )
                )
                return

            out_samples = b''.join(samples)
            out_pix = pymupdf.Pixmap(
                pymupdf.csRGB, target_width, total_height, out_samples, False
            )

            progress_queue.put(('progress', 3, 3, _('Saving...')))
            progress_queue.put(('progress', 3, 3, _('Done')))
            out_pix.save(output_path, jpg_quality=QUALITY)

            summary = _('Created long image from {} page(s): {}').format(
                len(pages),
                output_path.name,
            )
            progress_queue.put(('done', summary))

    except Exception as exc:  # surface any unexpected failure
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_pdf_to_long_image_with_progress(master, params: dict) -> None:
    """Run the render in a subprocess and show progress via ProgressDialog."""

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

    dialog = ProgressDialog(
        master,
        title=_('PDF to Long Image'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
