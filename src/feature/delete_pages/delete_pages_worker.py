"""Delete pages worker.

Deletes pages specified by a page-range expression from a single input PDF and
writes the result into an output folder. The expression uses the same syntax
as split_pdf's custom-range mode (see ``util.page_range_parser``) but each
';' group is treated as a SET OF PAGES TO DELETE, producing one output PDF
per group.

This is the complement of split_pdf's custom-range mode:
  split   -> keep the specified pages, one file per ';' group
  delete  -> delete the specified pages, one file per ';' group

Enhanced mode (+) is intentionally NOT supported for this feature.

Progress is counted per generated file (one per ';' group).
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror
from util.helpers import prompt_open_output

import pymupdf

from core.progress_dialog import ProgressDialog
from util.i18n import gettext_text as _


def worker(params: dict, progress_queue: Queue, cancel_event) -> None:
    """Delete pages per group and report progress per generated file.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary_message)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']

    src = Path(inputs[0])
    groups = options['groups']
    raw_groups = options['raw_groups']

    with pymupdf.open(src) as doc:
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        total_outputs = len(groups)
        if total_outputs == 0:
            progress_queue.put(('error', _('No groups to process.')))
            return

        failures = []
        produced = 0

        for idx, del_pages in enumerate(groups, start=1):
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            gexpr = raw_groups[idx - 1] if raw_groups else ''
            name = f'{src.stem}.D{gexpr.replace(":", "S")}.pdf'
            try:
                del_set = set(del_pages)
                with pymupdf.open() as out_doc:
                    for p in range(doc.page_count):
                        if p not in del_set:
                            out_doc.insert_pdf(doc, from_page=p, to_page=p)
                    out_doc.save(out_dir / name)
                produced += 1
            except Exception as exc:
                failures.append((name, f'{type(exc).__name__}: {exc}'))

            # Report progress per generated file (per ';' group).
            progress_queue.put(
                (
                    'progress',
                    idx,
                    total_outputs,
                    f'{_("Deleting...")} {idx}/{total_outputs}',
                )
            )

        if produced == 0:
            progress_queue.put(('error', _('No output files were written.')))
            return

        summary = _('Delete Pages') + f' ({produced}/{total_outputs})'
        if failures:
            summary += (
                '\n' + _('Failed:') + ' ' + '; '.join(f'{n}: {e}' for n, e in failures)
            )
        progress_queue.put(('progress', total_outputs, total_outputs, _('Done')))
        progress_queue.put(('done', summary))


def run_delete_pages_with_progress(master, params: dict) -> None:
    """Run delete-pages in a subprocess and show progress via ProgressDialog."""

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
        title=_('Delete Pages'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
