"""PDF to Images worker.

Multi-input -> output folder. For each input PDF a subfolder named after the
PDF's stem is created, and every page is rendered as ``{stem}.P{page}.{ext}``
(page is 1-based). PNG keeps transparency when requested; JPEG ignores
transparency and uses the quality setting. Mirrors the shared
Queue/Event/ProgressDialog scaffolding; a single failed file is skipped and
counted into the summary.
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
    """Render each input PDF's pages to image files.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params.get('inputs', [])
    output = params.get('output')
    options = params.get('options', {})
    dpi = int(options.get('dpi', 200))
    fmt = options.get('fmt', 'png')
    transparent = bool(options.get('transparent', False))
    quality = int(options.get('quality', 85))

    try:
        total = len(inputs)
        if total == 0:
            progress_queue.put(('error', _('No input files.')))
            return

        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        files_done = 0
        files_failed = 0
        pages_done = 0
        ext = 'png' if fmt == 'png' else 'jpg'
        # JPEG cannot carry an alpha channel; transparency only applies to PNG.
        alpha = (fmt == 'png') and bool(transparent)

        for index, in_path in enumerate(inputs, start=1):
            if cancel_event.is_set():
                progress_queue.put(('cancelled', None))
                return

            src = Path(in_path)
            progress_queue.put(
                ('progress', index, total,
                 f'{_("Converting...")} {index}/{total}')
            )

            try:
                doc = pymupdf.open(str(src))
                try:
                    stem = src.stem
                    sub = out_dir / stem
                    sub.mkdir(parents=True, exist_ok=True)

                    for p_idx, page in enumerate(doc, start=1):
                        pix = page.get_pixmap(dpi=dpi, alpha=alpha)
                        if fmt == 'jpg':
                            pix.save(
                                str(sub / f'{stem}.P{p_idx}.jpg'),
                                jpg_quality=quality,
                            )
                        else:
                            pix.save(str(sub / f'{stem}.P{p_idx}.png'))
                        pages_done += 1
                finally:
                    doc.close()
                files_done += 1
            except Exception as exc:
                files_failed += 1
                progress_queue.put(
                    ('progress', index, total,
                     f'{_("Failed")}: {src.name} ({type(exc).__name__}: {exc})')
                )

        summary = _('Converted %d page(s) from %d file(s) to images.') % (
            pages_done, files_done)
        if files_failed:
            summary += ' ' + (_('%d file(s) failed.') % files_failed)
        if files_done == 0 and total > 0:
            progress_queue.put(('error', summary))
            return

        progress_queue.put(('progress', total, total, _('Done')))
        progress_queue.put(('done', summary))

    except Exception as exc:  # surface any unexpected failure
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_pdf_to_images_with_progress(master, params: Dict[str, Any]) -> None:
    """Run the rendering in a subprocess and show progress via ProgressDialog."""
    from core.progress_dialog import ProgressDialog

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    state = {'finished': False}

    dialog = ProgressDialog(
        master,
        title=_('PDF to Images'),
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
