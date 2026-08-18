"""Encrypt PDF worker.

Each input PDF is encrypted independently (AES-256) with the user-supplied
password and written to the output folder as ``{stem}.{_('Encrypt')}.pdf``.
Inputs are processed as a batch (unordered); a file that fails is skipped and
reported in the final summary rather than aborting the whole run.
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showwarning
from util.helpers import prompt_open_output

import pymupdf

from core.progress_dialog import ProgressDialog
from util.i18n import gettext_text as _


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict, progress_queue: Queue, cancel_event) -> None:
    """Encrypt every input PDF and write results into the output folder.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_folder)
        ('partial', output_folder, success_count, failed_count, summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    password = options['password']

    try:
        total = len(inputs)
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        failed = []
        success_count = 0

        for index, in_path in enumerate(inputs, start=1):
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            src = Path(in_path)
            progress_queue.put(
                ('progress', index - 1, total, f'{_("Encrypting...")} {index}/{total}')
            )

            try:
                with pymupdf.open(src) as doc:
                    # An already-encrypted source needs its existing password
                    # before it can be re-saved; we only have the *new* password
                    # field, so re-encrypting is out of scope — fail clearly.
                    if doc.is_encrypted:
                        raise ValueError(_('Source PDF is already encrypted.'))
                    out_name = src.with_suffix(f'.{_("Encrypt")}.pdf').name
                    out_path = out_dir / out_name
                    doc.save(
                        out_path,
                        encryption=pymupdf.PDF_ENCRYPT_AES_256,
                        # type: ignore[attr-defined]  # 常量运行时存在(PyMuPDF 1.28.2)，仅 basedpyright 桩缺失
                        user_pw=password,
                        owner_pw=password,
                    )
                success_count += 1
            except Exception as exc:  # keep going, report at the end
                failed.append((src.name, f'{type(exc).__name__}: {exc}'))

        progress_queue.put(('progress', total, total, _('Done')))
        if failed:
            summary = _('{count} file(s) failed:').format(count=len(failed))
            for name, message in failed:
                summary += f'\n- {name}: {message}'
            progress_queue.put(
                ('partial', str(out_dir), success_count, len(failed), summary)
            )
        else:
            progress_queue.put(('done', str(out_dir)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_encrypt_with_progress(master, params: dict) -> None:
    """Run the encryption in a subprocess and show progress via ProgressDialog."""

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
        nonlocal finished
        cancel_event.set()
        if process is not None and process.is_alive():
            process.terminate()
        _finish()

    dialog = ProgressDialog(
        master,
        title=_('Encrypt PDF'),
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
                elif kind == 'partial':
                    _out_dir, _ok, _fail, summary = msg[1], msg[2], msg[3], msg[4]
                    _finish()
                    showwarning(title=_('Done with errors'), message=summary)
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
