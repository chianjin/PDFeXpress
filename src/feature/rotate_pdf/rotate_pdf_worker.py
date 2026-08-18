"""Rotate PDF worker.

The heavy rotation runs in a separate process (``worker``) so the UI stays
responsive. Progress is reported back to the main thread through a
``multiprocessing.Queue``, and the main thread shows it via
``core.progress_dialog.ProgressDialog`` (see ``run_rotate_with_progress``).

Each input PDF is rotated independently and written to the output folder.
Rotation is *relative*: every page keeps its existing ``/Rotate`` value and
the user-chosen delta is added, normalized to 0..359.
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
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict, progress_queue: Queue, cancel_event) -> None:
    """Rotate every input PDF and write results into the output folder.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_folder)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    delta = options['delta']

    try:
        # Granularity: per page across all input documents.
        total = 0
        for in_path in inputs:
            with pymupdf.open(Path(in_path)) as doc:
                total += doc.page_count
        if total == 0:
            progress_queue.put(('error', _('No pages to rotate.')))
            return

        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        done = 0
        for in_path in inputs:
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            src = Path(in_path)
            with pymupdf.open(src) as doc:
                # Relative, per-page rotation. PDF /Rotate (and page.rotation)
                # is clockwise-positive, matching the option value, so we add
                # the value as-is.
                for page in doc:
                    new_rotation = (page.rotation + delta) % 360
                    page.set_rotation(new_rotation)
                    done += 1
                    progress_queue.put(
                        ('progress', done, total, f'{_("Rotating...")} {done}/{total}')
                    )

                out_name = src.with_suffix(f'.{_("Rotate")}{delta}.pdf').name
                out_path = out_dir / out_name
                doc.save(out_path)

        progress_queue.put(('progress', total, total, _('Done')))
        progress_queue.put(('done', str(out_dir)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_rotate_with_progress(master, params: dict) -> None:
    """Run the rotation in a subprocess and show progress via ProgressDialog."""

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

    dialog = ProgressDialog(
        master,
        title=_('Rotate PDF'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
