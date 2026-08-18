"""Quick compress worker.

Multi-input PDF -> output folder, one compressed ``{stem}.{_('Compress')}.pdf``
per input (one-to-one). Uses the built-in cleanup pipeline:
``doc.save(out, garbage=4, clean=True, deflate=True, deflate_images=True,
deflate_fonts=True)`` — no embedded-image re-encoding.

Progress is counted per file. A single failed file is skipped and counted
into the summary.
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror
from util.helpers import prompt_open_output

import pymupdf

from core.progress_dialog import ProgressDialog
from util.i18n import gettext_text as _


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict, progress_queue: Queue, cancel_event) -> None:
    """Quick-compress every input PDF into the output folder.

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
        if total == 0:
            progress_queue.put(('error', _('No input files.')))
            return

        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        files_done = 0
        files_failed = 0

        for index, in_path in enumerate(inputs, start=1):
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            src = Path(in_path)
            progress_queue.put(
                ('progress', index - 1, total, f'{_("Compressing...")} {index}/{total}')
            )

            try:
                with pymupdf.open(src) as doc:
                    out_file = out_dir / f'{src.stem}.{_("Compress")}.pdf'
                    doc.save(
                        out_file,
                        garbage=4,
                        clean=True,
                        deflate=True,
                        deflate_images=True,
                        deflate_fonts=True,
                    )
                files_done += 1
            except Exception as exc:
                files_failed += 1
                progress_queue.put(
                    (
                        'progress',
                        index - 1,
                        total,
                        _('Failed: {} ({}: {})').format(
                            src.name, type(exc).__name__, exc
                        ),
                    )
                )

        summary = _('Compressed {} file(s).').format(files_done)
        if files_failed:
            summary += ' ' + (_('{} file(s) failed.').format(files_failed))
        if files_done == 0 and total > 0:
            progress_queue.put(('error', summary))
            return

        progress_queue.put(('progress', total, total, _('Done')))
        progress_queue.put(('done', summary))

    except Exception as exc:
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_quick_compress_with_progress(master, params: dict) -> None:
    """Run quick compression in a subprocess with a progress dialog."""

    progress_queue: Queue = Queue()
    cancel_event = Event()
    process = None
    finished = False

    def _on_cancel():
        cancel_event.set()
        if process is not None and process.is_alive():
            process.terminate()
        _finish()

    def _finish():
        nonlocal finished
        if finished:
            return
        finished = True
        if process is not None and process.is_alive():
            process.join(timeout=2)
        dialog.destroy()

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
        title=_('Quick Compress'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
