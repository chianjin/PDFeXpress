"""PDF interleave merge worker.

Two input PDFs (A = inputs[0], B = inputs[1]) are merged page-by-page in an
interleaved order: A1, B1, A2, B2, ... PDF B may be reversed. When one file
runs out of pages, the remaining pages of the longer file are appended as a
block. The heavy work runs in a separate process so the UI stays responsive;
progress is reported back through a multiprocessing.Queue and shown via
``core.progress_dialog.ProgressDialog`` (see ``run_interleave_with_progress``).
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
def worker(params: dict, progress_queue: Queue, cancel_event: Event) -> None:
    """Interleave-merge inputs[0]=A and inputs[1]=B and report progress.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_path)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    reverse_b = options['reverse_b']

    try:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with pymupdf.open(inputs[0]) as a, pymupdf.open(inputs[1]) as b:
            len_a = a.page_count
            len_b = b.page_count
            # B page order: reversed when requested, else forward.
            b_order = (
                list(range(len_b - 1, -1, -1)) if reverse_b else list(range(len_b))
            )
            total = len_a + len_b

            with pymupdf.open() as out:
                done = 0
                for i in range(max(len_a, len_b)):
                    if cancel_event.is_set():
                        progress_queue.put(('cancelled', None))
                        return

                    if i < len_a:
                        out.insert_pdf(a, from_page=i, to_page=i)
                    if i < len_b:
                        out.insert_pdf(b, from_page=b_order[i], to_page=b_order[i])
                    done += (1 if i < len_a else 0) + (1 if i < len_b else 0)
                    progress_queue.put(
                        ('progress', done, total, f'{_("Interleaving...")} {done}/{total}')
                    )

                progress_queue.put(('progress', total, total, _('Saving...')))
                out.save(output_path)
                progress_queue.put(('done', str(output_path)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_interleave_with_progress(master, params: dict) -> None:
    """Run the interleave merge in a subprocess and show progress via ProgressDialog."""

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
        title=_('Interleave Merge'),
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
                    showinfo(
                        title=_('Done'),
                        message=_('PDF Interleaved'),
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

        if not finished:
            master.after(100, _poll)

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
