"""Split PDF worker.

Splits a single input PDF into multiple output PDFs saved into an output
folder. Four modes: single page, by page count, by parts, custom range.

The heavy work runs in a separate process (``worker``) so the UI stays
responsive. Progress is reported back to the main thread through a
``multiprocessing.Queue``, and the main thread shows it via
``core.progress_dialog.ProgressDialog`` (see ``run_split_with_progress``).

Custom-range parsing (``util.page_range_parser.parse_page_ranges``) is done
in the frame, so the worker receives already-resolved ``list[list[int]]`` of
0-based page indices; see ``split_pdf_frame``.
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo

import pymupdf

from core.progress_dialog import ProgressDialog
from util.i18n import gettext_text as _


# ---------------------------------------------------------------------------
# Chunk building (pure logic)
# ---------------------------------------------------------------------------
def _build_chunks(mode, options, total):
    """Return a list of chunks; each chunk is a list of 0-based page indices."""
    if mode == 'single':
        return [[i] for i in range(total)]

    if mode == 'by_pages':
        n = options['pages_per_chunk']
        if n < 1:
            raise ValueError(_('Pages per chunk must be at least 1.'))
        chunks = []
        for start in range(0, total, n):
            chunks.append(list(range(start, min(start + n, total))))
        return chunks

    if mode == 'by_parts':
        k = options['parts']
        if k < 1:
            raise ValueError(_('Number of parts must be at least 1.'))
        if k > total:
            raise ValueError(_('Number of parts cannot exceed total pages.'))
        base = total // k
        extra = total % k
        chunks = []
        begin = 0
        for i in range(k):
            size = base + (1 if i < extra else 0)
            chunks.append(list(range(begin, begin + size)))
            begin += size
        return chunks

    if mode == 'custom':
        groups = options['groups']
        if not groups:
            raise ValueError(_('Range expression produced no pages.'))
        return groups

    raise ValueError(_('Unknown split mode.'))


def _chunk_name(mode, stem, chunk, width, group_expr=None):
    """Build the output filename for one chunk.

    - single:        P{1-based page}, e.g. P001.pdf
    - by_pages/parts: P{start}-{end} (1-based, zero-padded to `width`)
    - custom:        R{group substring with ':' replaced by 'S'}
    """
    if mode == 'single':
        page_no = chunk[0] + 1
        return f'{stem}.P{page_no:0{width}d}.pdf'
    if mode in ('by_pages', 'by_parts'):
        start = chunk[0] + 1
        end = chunk[-1] + 1
        return f'{stem}.P{start:0{width}d}-{end:0{width}d}.pdf'
    if mode == 'custom':
        safe = (group_expr or '').replace(':', 'S')
        return f'{stem}.R{safe}.pdf'
    raise ValueError(_('Unknown split mode.'))


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params, progress_queue, cancel_event):
    """Split the input PDF and write results into the output folder.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary_message)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']

    try:
        src = Path(inputs[0])
        mode = options['mode']

        with pymupdf.open(src) as doc:
            total = options['total_pages']
            width = len(str(total))  # zero-padding width = digits of total

            chunks = _build_chunks(mode, options, total)
            group_exprs = options.get('group_exprs') or []

            out_dir = Path(output)
            out_dir.mkdir(parents=True, exist_ok=True)

            total_outputs = len(chunks)
            if total_outputs == 0:
                progress_queue.put(('error', _('Nothing to split.')))
                return

            failures = []
            produced = 0
            for idx, chunk in enumerate(chunks, start=1):
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return

                if mode == 'custom':
                    gexpr = group_exprs[idx - 1] if group_exprs else ''
                    name = _chunk_name(mode, src.stem, chunk, width, gexpr)
                else:
                    name = _chunk_name(mode, src.stem, chunk, width)

                progress_queue.put(
                    (
                        'progress',
                        idx,
                        total_outputs,
                        f'{_("Splitting……")} {idx}/{total_outputs}',
                    )
                )

                try:
                    with pymupdf.open() as out_doc:
                        for p in chunk:
                            out_doc.insert_pdf(doc, from_page=p, to_page=p)
                        out_doc.save(out_dir / name)
                    produced += 1
                except Exception as exc:  # skip this file, summarize later
                    failures.append((name, f'{type(exc).__name__}: {exc}'))

            if produced == 0:
                progress_queue.put(('error', _('No output files were written.')))
                return

            summary = _('PDF Split') + f' ({produced}/{total_outputs})'
            if failures:
                summary += (
                    '\n'
                    + _('Failed:')
                    + ' '
                    + '; '.join(f'{n}: {e}' for n, e in failures)
                )
            progress_queue.put(('progress', total_outputs, total_outputs, _('Done')))
            progress_queue.put(('done', summary))

    except Exception as exc:  # surface any failure (bad range, etc.) to the UI
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_split_with_progress(master, params):
    """Run the split in a subprocess and show progress via ProgressDialog."""

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
        title=_('Split PDF'),
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
