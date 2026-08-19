"""Divide PDF pages worker.

Every page is split into N equal strips and the strips are reassembled as
a new PDF. The UI directions are interpreted in *visual* space (what the
reader sees):

* ``direction='vertical'``: strips are the visual left-to-right columns
  (a landscape A3 page divided into 2 becomes two portrait A4 pages).
* ``direction='horizontal'``: strips are the visual top-to-bottom rows.

For pages carrying a /Rotate attribute the split is still performed on the
visual page: each visual strip is mapped to the page's unrotated
coordinates via ``derotation_matrix``, the source page is temporarily reset
to 0 degrees while the clip is applied, and each output page keeps the
original rotation. Output order is the visual reading order (first page =
visual leftmost/topmost strip); no reordering is needed.

Source content is reused as Form XObjects via show_pdf_page, so raster
images are embedded once and text stays selectable. Saving with
garbage=3 + deflate deduplicates identical objects, keeping the output
close to the source size for image/scan documents.

Runs in a subprocess so the UI stays responsive; progress is reported per
original page through a ``multiprocessing.Queue`` and shown via
``core.progress_dialog.ProgressDialog``.
"""

from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror

import pymupdf

from core.progress_dialog import ProgressDialog
from util.helpers import prompt_open_output
from util.i18n import gettext_text as _


def _visual_strips(r: pymupdf.Rect, direction: str, parts: int):
    """Yield visual strips of the displayed page in reading order."""
    if direction == 'horizontal':
        step = r.height / parts
        for i in range(parts):
            yield pymupdf.Rect(0, i * step, r.width, (i + 1) * step)
    else:  # vertical
        step = r.width / parts
        for i in range(parts):
            yield pymupdf.Rect(i * step, 0, (i + 1) * step, r.height)


def worker(params: dict, progress_queue: Queue, cancel_event) -> None:
    direction = params['options']['direction']
    parts = params['options']['parts']
    try:
        src = Path(params['inputs'][0])
        out_path = Path(params['output'])
        with pymupdf.open(src) as src_doc:
            total = len(src_doc)
            with pymupdf.open() as out_doc:
                for idx in range(total):
                    if cancel_event.is_set():
                        progress_queue.put(('cancelled', None))
                        return
                    progress_queue.put(
                        (
                            'progress',
                            idx,
                            total,
                            f'{_("Dividing...")} {idx + 1}/{total}',
                        )
                    )
                    sp = src_doc[idx]
                    r = sp.rect  # 显示尺寸（含旋转）
                    rotation = sp.rotation
                    derotation = sp.derotation_matrix  # 显示坐标 -> raw 坐标
                    sp.set_rotation(0)  # 源页带 /Rotate 时 clip 行为不可靠，先恢复 0°
                    for vs in _visual_strips(r, direction, parts):
                        raw = vs * derotation
                        pg = out_doc.new_page(width=raw.width, height=raw.height)
                        pg.show_pdf_page(pg.rect, src_doc, idx, clip=raw)
                        pg.set_rotation(rotation)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_doc.save(out_path, garbage=3, deflate=True)
            progress_queue.put(('progress', total, total, _('Done')))
            progress_queue.put(('done', str(out_path)))
    except Exception as exc:
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


def run_divide_pages_with_progress(master, params: dict) -> None:
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
        title=_('Divide Pages'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    def _poll():
        if finished:
            return
        try:
            while True:
                msg = progress_queue.get_nowait()
                kind = msg[0]
                if kind == 'progress':
                    _i, cur, tot, text = msg
                    dialog.set_progress((cur / tot) if tot else 0, text)
                elif kind == 'done':
                    _finish()
                    prompt_open_output(master, msg[1])
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
