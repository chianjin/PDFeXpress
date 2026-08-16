"""Extract images worker.

Multi-input -> output folder. For each input PDF a subfolder named after the
PDF's stem (no suffix) is created under the output folder, and every embedded
image is saved there as raw bytes with a name ``{stem}.P{page}-{xref}.{ext}``
(page is 1-based, xref is the image's xref in the PDF, ext comes from the
image's internal format). Optionally images smaller than a pixel threshold
are skipped. Mirrors ``rotate_pdf_worker`` for the process/queue/dialog
scaffolding; a single failed file is skipped and counted into the summary.
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo

import pymupdf

from core.progress_dialog import ProgressDialog
from util.i18n import gettext_text as _


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict, progress_queue: Queue, cancel_event) -> None:
    """Extract images from every input PDF into per-file subfolders.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    ignore_small = options['ignore_small']
    min_w = options['min_w']
    min_h = options['min_h']

    try:
        total = len(inputs)
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        files_done = 0
        files_failed = 0
        images_extracted = 0
        images_skipped = 0

        for index, in_path in enumerate(inputs, start=1):
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            src = Path(in_path)
            progress_queue.put(
                (
                    'progress',
                    index,
                    total,
                    f'{_("Extracting...")} {index}/{total}',
                )
            )

            try:
                with pymupdf.open(src) as doc:
                    stem = src.stem
                    sub = out_dir / stem
                    sub.mkdir(parents=True, exist_ok=True)

                    for p_idx, page in enumerate(doc, start=1):
                        seen = set()
                        for img_info in page.get_images(full=True):
                            xref = img_info[0]
                            if xref in seen:
                                continue
                            seen.add(xref)

                            img = doc.extract_image(xref)
                            w = img.get('width', 0) or 0
                            h = img.get('height', 0) or 0
                            if ignore_small and (w < min_w or h < min_h):
                                images_skipped += 1
                                continue

                            ext = img.get('ext') or 'png'
                            data = img.get('image')
                            if not data:
                                continue

                            fname = f'{stem}.P{p_idx}-{xref}.{ext}'
                            (sub / fname).write_bytes(data)
                            images_extracted += 1
                files_done += 1
            except Exception as exc:
                files_failed += 1
                progress_queue.put(
                    (
                        'progress',
                        index,
                        total,
                        f'{_("Failed")}: {src.name} ({type(exc).__name__}: {exc})',
                    )
                )

        summary = _('Extracted {} image(s) from {} file(s).').format(
            images_extracted,
            files_done,
        )
        if images_skipped:
            summary += ' ' + (_('{} small image(s) skipped.').format(images_skipped))
        if files_failed:
            summary += ' ' + (_('{} file(s) failed.').format(files_failed))
        if files_done == 0 and total > 0:
            progress_queue.put(('error', summary))
            return

        progress_queue.put(('progress', total, total, _('Done')))
        progress_queue.put(('done', summary))

    except Exception as exc:  # surface any unexpected failure
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_extract_images_with_progress(master, params: dict) -> None:
    """Run image extraction in a subprocess and show progress via ProgressDialog."""

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
        title=_('Extract Images'),
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
                    showinfo(title=_('Done'), message=msg[1])
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
