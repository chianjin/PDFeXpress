"""PDF merge worker.

The heavy merge runs in a separate process (``worker``) so the UI stays
responsive. Progress is reported back to the main thread through a
``multiprocessing.Queue``, and the main thread shows it via
``core.progress_dialog.ProgressDialog`` (see ``run_merge_with_progress``).
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
    """Merge input PDFs into one output PDF and report progress.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_path)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params.get('inputs', [])
    output = params.get('output')
    options = params.get('options', {})
    generate_bookmarks = bool(options.get('generate_bookmarks', False))
    support_delux_print = bool(options.get('support_delux_print', False))

    try:
        total = len(inputs)
        if total == 0:
            progress_queue.put(('error', _('No input files.')))
            return

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        out = pymupdf.open()
        toc = []  # bookmark entries: [level, title, page(1-based)]

        for index, in_path in enumerate(inputs, start=1):
            if cancel_event.is_set():
                out.close()
                progress_queue.put(('cancelled', None))
                return

            src_path = Path(in_path)
            progress_queue.put(
                ('progress', index, total,
                 f'{_("Merging")} ({index}/{total}): {src_path.name}')
            )

            src = pymupdf.open(str(src_path))
            try:
                start_page = out.page_count  # 0-based
                out.insert_pdf(src)
                if generate_bookmarks:
                    toc.append([1, src_path.stem, start_page + 1])  # 1-based
            finally:
                src.close()

            if cancel_event.is_set():
                out.close()
                progress_queue.put(('cancelled', None))
                return

        if generate_bookmarks and toc:
            out.set_toc(toc)

        if support_delux_print:
            # Best-effort: configure viewer print preferences. Failure here
            # must not break the merge, so it is swallowed.
            try:
                catalog = out.pdf_catalog()
                out.xref_set_key(
                    catalog, '/ViewerPreferences',
                    '<< /PrintScaling /None /PickTrayByPDFSize true >>'
                )
            except Exception:
                pass

        progress_queue.put(('progress', total, total, _('Saving...')))
        out.save(str(output_path))
        out.close()
        progress_queue.put(('done', str(output_path)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_merge_with_progress(master, params: Dict[str, Any]) -> None:
    """Run the merge in a subprocess and show progress via ProgressDialog."""
    # Lazy import so the subprocess (which re-imports this module under
    # spawn) does not pay the cost of importing tkinter.
    from core.progress_dialog import ProgressDialog

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    state = {'finished': False}

    dialog = ProgressDialog(
        master,
        title=_('Merging PDFs'),
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
                    _, current, total, text = msg
                    fraction = (current / total) if total else 0
                    dialog.set_progress(fraction, text)
                elif kind == 'done':
                    _, out_path = msg
                    _finish()
                    showinfo(
                        title=_('Done'),
                        message=_('Merged PDF saved to:\n%s') % out_path,
                    )
                    return
                elif kind == 'error':
                    _, err = msg
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
