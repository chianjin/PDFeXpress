"""PDF merge worker.

The heavy merge runs in a separate process (``worker``) so the UI stays
responsive. Progress is reported back to the main thread through a
``multiprocessing.Queue``, and the main thread shows it via
``core.progress_dialog.ProgressDialog`` (see ``run_merge_with_progress``).
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
    """Merge input PDFs into one output PDF and report progress.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', output_path)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    generate_bookmarks = options['generate_bookmarks']
    support_delux_print = options['support_delux_print']
    total = len(inputs)

    try:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with pymupdf.open() as out:
            toc = []  # bookmark entries: [level, title, page(1-based)]

            for index, in_path in enumerate(inputs, start=1):
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return

                src_path = Path(in_path)
                progress_queue.put(
                    ('progress', index - 1, total, f'{_("Merging...")} {index}/{total}')
                )

                with pymupdf.open(src_path) as src:
                    # Deluxe (double-sided) print: every source PDF's first
                    # page must land on an ODD page (1-based) so each original
                    # PDF stays independently bound after printing. The next
                    # inserted page will be at 0-based position out.page_count;
                    # its 1-based number is out.page_count + 1. To make that odd
                    # we need out.page_count even, so pad a blank page when odd.
                    if support_delux_print and out.page_count % 2 == 1:
                        if src.page_count:
                            rect = src[0].rect
                            out.new_page(width=rect.width, height=rect.height)
                        else:
                            out.new_page()

                    start_page = out.page_count  # 0-based
                    out.insert_pdf(src)
                    if generate_bookmarks:
                        toc.append([1, src_path.stem, start_page + 1])  # 1-based

                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return

            if generate_bookmarks and toc:
                out.set_toc(toc)

            progress_queue.put(('progress', total, total, _('Saving...')))
            progress_queue.put(('progress', total, total, _('Done')))
            out.save(output_path)
            progress_queue.put(('done', str(output_path)))

    except Exception as exc:  # surface any failure to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_merge_with_progress(master, params: dict) -> None:
    """Run the merge in a subprocess and show progress via ProgressDialog."""

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
        title=_('Merge PDF'),
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
