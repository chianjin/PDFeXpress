"""Extract text worker.

Multi-input -> output folder, one ``.txt`` per PDF (plain UTF-8, no BOM).
The heavy extraction runs in a subprocess so the UI stays responsive;
progress is reported through a ``multiprocessing.Queue`` and shown via
``core.progress_dialog.ProgressDialog``. A single failed file is skipped and
counted into the summary (B-type "skip + summarize" convention).
"""

import pymupdf
from multiprocessing import Process, Queue, Event
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo

from util.i18n import gettext_text as _


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict, progress_queue: Queue, cancel_event: Event) -> None:
    """Extract text from every input PDF into the output folder.

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
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        processed = 0
        failed = 0

        for index, in_path in enumerate(inputs, start=1):
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            src = Path(in_path)
            progress_queue.put(
                ('progress', index, total,
                 f'{_("Extracting text……")} {index}/{total}')
            )

            try:
                doc = pymupdf.open(str(src))
                try:
                    text = "".join(page.get_text() for page in doc)
                finally:
                    doc.close()

                out_name = src.with_suffix('.txt').name
                out_path = out_dir / out_name
                out_path.write_text(text, encoding='utf-8')  # plain UTF-8, no BOM
                processed += 1
            except Exception as exc:
                failed += 1
                progress_queue.put(
                    ('progress', index, total,
                     f'{_("Failed")}: {src.name} ({type(exc).__name__}: {exc})')
                )

        summary = _('Text extracted from %d of %d file(s).') % (processed, total)
        if failed:
            summary += ' ' + (_('%d file(s) failed.') % failed)
        if processed == 0 and total > 0:
            progress_queue.put(('error', summary))
            return

        progress_queue.put(('progress', total, total, _('Done')))
        progress_queue.put(('done', summary))

    except Exception as exc:  # surface any unexpected failure
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_extract_text_with_progress(master, params: dict) -> None:
    """Run text extraction in a subprocess and show progress via ProgressDialog."""
    from core.progress_dialog import ProgressDialog

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
        title=_('Extract Text'),
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
