"""Decrypt PDF worker.

A single encrypted PDF is opened, authenticated with the supplied password,
and re-saved without encryption (AES-256 -> plain). If the password is wrong
or missing, the operation fails with a clear message.
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
    """Decrypt the single input PDF and write the plain result.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_path)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params.get('inputs', [])
    output = params.get('output')
    options = params.get('options', {})
    password = options.get('password', '') or ''

    try:
        if len(inputs) < 1:
            progress_queue.put(('error', _('No input file.')))
            return
        if cancel_event.is_set():
            progress_queue.put(('cancelled', None))
            return

        src = Path(inputs[0])
        progress_queue.put(('progress', 1, 1, _('Decrypting……')))

        doc = pymupdf.open(str(src))
        try:
            if doc.is_encrypted and doc.authenticate(password) == 0:
                raise ValueError(_('Wrong password or password required.'))
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(out_path))
        finally:
            doc.close()

        progress_queue.put(('progress', 1, 1, _('Done')))
        progress_queue.put(('done', str(output)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_decrypt_with_progress(master, params: Dict[str, Any]) -> None:
    """Run the decryption in a subprocess and show progress via ProgressDialog."""
    from core.progress_dialog import ProgressDialog

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    state = {'finished': False}

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

    dialog = ProgressDialog(
        master,
        title=_('Decrypt PDF'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

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
                    showinfo(title=_('Done'), message=_('PDF Decrypted'))
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
