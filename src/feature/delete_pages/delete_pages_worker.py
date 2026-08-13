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

The heavy work runs in a separate process (``worker``) so the UI stays
responsive. Progress is reported back through a ``multiprocessing.Queue`` and
shown via ``core.progress_dialog.ProgressDialog`` (see ``run_delete_with_progress``).
"""

import pymupdf
from multiprocessing import Process, Queue, Event
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo

from util.i18n import gettext_text as _
from util.page_range_parser import parse_page_ranges


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params, progress_queue, cancel_event):
    """Delete pages per group and write results into the output folder.

    Messages (same contract as split_pdf_worker.worker):
        ('progress', current, total, message)
        ('done', summary_message)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params.get('inputs', [])
    output = params.get('output')
    options = params.get('options', {})

    try:
        if not inputs:
            progress_queue.put(('error', _('No input files.')))
            return
        src = Path(inputs[0])
        if not src.is_file():
            progress_queue.put(('error', _('Input PDF does not exist.')))
            return

        expr = options.get('range_expr', '').strip()
        if not expr:
            progress_queue.put(('error', _('Pages to delete must be set.')))
            return
        if expr.startswith('+'):
            progress_queue.put(('error', _('Enhanced mode (+) is not supported.')))
            return

        doc = pymupdf.open(str(src))
        try:
            total = doc.page_count

            # Raw group substrings (for naming), in parser order; each group is
            # a set of pages to DELETE. parse_page_ranges returns
            # list[list[int]] of 0-based pages per ';' group; we treat each as
            # the pages to remove.
            raw_groups = [g.strip() for g in expr.split(';') if g.strip()]
            groups = parse_page_ranges(expr, total)
            if not groups:
                progress_queue.put(('error', _('Range expression produced no pages.')))
                return
            if len(groups) != len(raw_groups):
                # Defensive only: keep naming aligned with produced groups.
                raw_groups = raw_groups[:len(groups)]

            out_dir = Path(output)
            out_dir.mkdir(parents=True, exist_ok=True)

            total_outputs = len(groups)
            failures = []
            produced = 0

            for idx, del_pages in enumerate(groups, start=1):
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return

                gexpr = raw_groups[idx - 1] if raw_groups else ''
                name = f"{src.stem}.D{gexpr.replace(':', 'S')}.pdf"

                progress_queue.put(
                    ('progress', idx, total_outputs,
                     f'{_("Deleting……")} {idx}/{total_outputs}')
                )

                try:
                    del_set = set(del_pages)
                    out_doc = pymupdf.open()
                    try:
                        for p in range(total):
                            if p not in del_set:
                                out_doc.insert_pdf(doc, from_page=p, to_page=p)
                        out_doc.save(str(out_dir / name))
                    finally:
                        out_doc.close()
                    produced += 1
                except Exception as exc:
                    failures.append((name, f'{type(exc).__name__}: {exc}'))

            if produced == 0:
                progress_queue.put(('error', _('No output files were written.')))
                return

            summary = _('Delete Pages') + f' ({produced}/{total_outputs})'
            if failures:
                summary += '\n' + _('Failed:') + ' ' + \
                    '; '.join(f'{n}: {e}' for n, e in failures)
            progress_queue.put(('progress', total_outputs, total_outputs, _('Done')))
            progress_queue.put(('done', summary))

        finally:
            doc.close()

    except Exception as exc:
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_delete_with_progress(master, params):
    """Run the delete in a subprocess and show progress via ProgressDialog."""
    from core.progress_dialog import ProgressDialog

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    state = {'finished': False}

    dialog = ProgressDialog(
        master,
        title=_('Delete Pages'),
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

        if not state['finished']:
            master.after(100, _poll)

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
