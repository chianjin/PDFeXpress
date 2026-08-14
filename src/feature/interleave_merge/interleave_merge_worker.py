"""PDF interleave merge worker.

Two input PDFs (A = inputs[0], B = inputs[1]) are merged page-by-page in an
interleaved order: A1, B1, A2, B2, ... PDF B may be reversed. When one file
runs out of pages, the remaining pages of the longer file are appended as a
block. The heavy work runs in a separate process so the UI stays responsive;
progress is reported back through a multiprocessing.Queue and shown via
``core.progress_dialog.ProgressDialog`` (see ``run_interleave_with_progress``).
"""

import pymupdf
from multiprocessing import Process, Queue, Event
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo
from typing import Any, Dict

from util.i18n import gettext_text as _


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: Dict[str, Any], progress_queue: Queue, cancel_event: Event) -> None:
    """Interleave-merge inputs[0]=A and inputs[1]=B and report progress.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_path)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params.get('inputs', [])
    output = params.get('output')
    options = params.get('options', {})
    reverse_b = bool(options.get('reverse_b', False))

    try:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        a = pymupdf.open(str(inputs[0]))
        b = pymupdf.open(str(inputs[1]))
        try:
            len_a = a.page_count
            len_b = b.page_count
            # B page order: reversed when requested, else forward.
            b_order = list(range(len_b - 1, -1, -1)) if reverse_b else list(range(len_b))
            total = len_a + len_b

            out = pymupdf.open()
            done = 0
            for i in range(max(len_a, len_b)):
                if cancel_event.is_set():
                    out.close()
                    progress_queue.put(('cancelled', None))
                    return

                if i < len_a:
                    out.insert_pdf(a, from_page=i, to_page=i)
                if i < len_b:
                    out.insert_pdf(b, from_page=b_order[i], to_page=b_order[i])
                done += (1 if i < len_a else 0) + (1 if i < len_b else 0)
                progress_queue.put(
                    ('progress', done, total,
                     f'{_("Interleaving...")} {done}/{total}')
                )

            progress_queue.put(('progress', total, total, _('Saving...')))
            out.save(str(output_path))
            out.close()
            progress_queue.put(('done', str(output_path)))
        finally:
            a.close()
            b.close()

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_interleave_with_progress(master, params: Dict[str, Any]) -> None:
    """Run the interleave merge in a subprocess and show progress via ProgressDialog."""
    # Lazy import so the subprocess (which re-imports this module under
    # spawn) does not pay the cost of importing tkinter.
    from core.progress_dialog import ProgressDialog

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    state = {'finished': False}

    dialog = ProgressDialog(
        master,
        title=_('Interleave Merge'),
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

        if not state['finished']:
            master.after(100, _poll)

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
