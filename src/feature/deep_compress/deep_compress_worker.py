"""Deep compress worker.

Single-input PDF -> single-output PDF. Every embedded image whose effective
resolution exceeds the configured maximum is downsampled via Pillow (LANCZOS)
to the target pixel size, re-encoded in its original format (png keeps
transparency, jpg uses the given quality), and replaced in place -- but only
if the re-encoded bytes are smaller than the original. Images in other formats
are skipped so the original format is preserved. Saving always uses the built-in
cleanup pipeline (garbage=4, clean=True, deflate=True, deflate_images=True,
deflate_fonts=True).

Progress is counted per page. A single failed file aborts with an error.
"""

import io
from multiprocessing import Event, Process, Queue
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror
from typing import Any

import pymupdf

from core.progress_dialog import ProgressDialog
from util.helpers import prompt_open_output
from util.i18n import gettext_text as _


def _downscale_page_images(doc, page, max_dpi: int, jpg_quality: int, ctr: dict[str, int]) -> None:
    """Downsample every over-resolution embedded image on ``page`` in place.

    ``ctr`` accumulates: downscaled / skipped_bigger / skipped_format.
    """
    from PIL import Image

    seen = set()
    for img_info in page.get_images(full=True):
        xref = img_info[0]
        if xref in seen:
            continue
        seen.add(xref)

        smask = img_info[1]
        info = doc.extract_image(xref)
        ext = (info.get('ext') or '').lower()
        if ext not in ('png', 'jpg', 'jpeg'):
            ctr['skipped_format'] += 1
            continue

        raw = info.get('image')
        if not raw:
            continue

        try:
            pix = pymupdf.Pixmap(raw)
        except Exception:
            ctr['skipped_format'] += 1
            continue

        raw_len = len(raw)
        if smask:
            try:
                mask_info = doc.extract_image(smask)
                mask_bytes = mask_info.get('image') or b''
                mask_pix = pymupdf.Pixmap(mask_bytes)
                pix = pymupdf.Pixmap(pix, mask_pix)
                raw_len += len(mask_bytes)
            except Exception:
                pass

        W, H = pix.width, pix.height
        rects = page.get_image_rects(xref)
        if not rects:
            ctr['skipped_format'] += 1
            continue
        rect_w = rects[0].width
        rect_h = rects[0].height
        dpi_x = 72.0 * W / rect_w if rect_w else 0.0
        dpi_y = 72.0 * H / rect_h if rect_h else 0.0
        eff_dpi = max(dpi_x, dpi_y)
        if eff_dpi <= max_dpi:
            continue  # already within budget

        factor = max_dpi / eff_dpi
        nw = max(1, round(W * factor))
        nh = max(1, round(H * factor))

        mode = {1: 'L', 2: 'LA', 3: 'RGB', 4: 'RGBA'}.get(pix.n, 'RGB')
        try:
            pil_img = Image.frombytes(mode, (W, H), pix.samples)
        except Exception:
            ctr['skipped_format'] += 1
            continue
        pil_img = pil_img.resize((nw, nh), Image.Resampling.LANCZOS)

        bio = io.BytesIO()
        if ext == 'png' or smask:
            # Keep PNG so transparency (stored as a separate SMask) is preserved.
            # replace_image() splits RGBA back into color + SMask automatically.
            if pil_img.mode in ('RGBA', 'LA'):
                pil_img = pil_img.convert('RGBA')
            pil_img.save(bio, format='PNG')
        else:
            pil_img = pil_img.convert('RGB')
            pil_img.save(bio, format='JPEG', quality=jpg_quality)
        new_bytes = bio.getvalue()

        if len(new_bytes) >= raw_len:
            ctr['skipped_bigger'] += 1
            continue

        try:
            page.replace_image(xref, stream=new_bytes)
            ctr['downscaled'] += 1
        except Exception:
            ctr['skipped_format'] += 1


# ---------------------------------------------------------------------------
# Subprocess: pure logic, no tkinter dependency.
# ---------------------------------------------------------------------------
def worker(params: dict[str, Any], progress_queue: Queue, cancel_event) -> None:
    """Deep-compress a single input PDF into the output path.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    max_dpi = options['max_dpi']
    jpg_quality = options['jpg_quality']

    try:
        if len(inputs) != 1:
            progress_queue.put(('error', _('Exactly one input PDF is required.')))
            return

        src = Path(inputs[0])
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with pymupdf.open(src) as doc:
            total = doc.page_count
            ctr = {'downscaled': 0, 'skipped_bigger': 0, 'skipped_format': 0}

            for p_idx in range(total):
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return
                progress_queue.put(
                    (
                        'progress',
                        p_idx,
                        total,
                        f'{_("Compressing...")} {p_idx + 1}/{total}',
                    )
                )
                _downscale_page_images(doc, doc[p_idx], max_dpi, jpg_quality, ctr)

            doc.save(
                output_path,
                garbage=4,
                clean=True,
                deflate=True,
                deflate_images=True,
                deflate_fonts=True,
            )

        summary = _('Compressed {} page(s) to: {}').format(total, output_path.name)
        summary += ' ' + (_('Downscaled {} image(s).').format(ctr['downscaled']))
        if ctr['skipped_bigger']:
            summary += ' ' + _('{} image(s) kept (new size not smaller).').format(ctr['skipped_bigger'])
        if ctr['skipped_format']:
            summary += ' ' + _('{} image(s) skipped (unsupported format).').format(ctr['skipped_format'])
        progress_queue.put(('progress', total, total, _('Done')))
        progress_queue.put(('done', summary))

    except Exception as exc:
        progress_queue.put(('error', f'{type(exc).__name__}: {exc}'))


# ---------------------------------------------------------------------------
# Main-thread controller: wires the dialog, the process and the queue.
# ---------------------------------------------------------------------------
def run_deep_compress_with_progress(master, params: dict[str, Any]) -> None:
    """Run deep compression in a subprocess and show progress via ProgressDialog."""

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
        title=_('Deep Compress'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
