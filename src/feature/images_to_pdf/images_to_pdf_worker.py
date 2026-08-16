"""Images to PDF worker.

Multi-image -> single PDF. Each image is opened, converted to a one-page PDF
with ``convert_to_pdf()`` and inserted into the output document in the exact
order received from the UI (no sorting). Runs in a subprocess with the shared
Queue/Event/ProgressDialog scaffolding.
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
    """Convert images to a single PDF.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']

    try:
        total = len(inputs)
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with pymupdf.open() as out:
            for index, in_path in enumerate(inputs, start=1):
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return

                src = Path(in_path)
                progress_queue.put(
                    ('progress', index, total, f'{_("Converting...")} {index}/{total}')
                )

                try:
                    with pymupdf.open(src) as img_doc:
                        pdf_bytes = img_doc.convert_to_pdf()
                        with pymupdf.open(stream=pdf_bytes, filetype='pdf') as pdf_doc:
                            out.insert_pdf(pdf_doc)
                except Exception as exc:
                    progress_queue.put(
                        ('error', f'{src.name}: {type(exc).__name__}: {exc}')
                    )
                    return

            progress_queue.put(('progress', total, total, _('Saving...')))
            progress_queue.put(('progress', total, total, _('Done')))
            out.save(output_path)

        summary = _('Converted {} image(s) to PDF: {}').format(total, output_path.name)
        progress_queue.put(('done', summary))

    except Exception as exc:  # surface any unexpected failure
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_images_to_pdf_with_progress(master, params: dict) -> None:
    """Run the conversion in a subprocess and show progress via ProgressDialog."""

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
        title=_('Images to PDF'),
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
