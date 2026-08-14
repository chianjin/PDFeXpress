"""Compress PDF worker.

Multi-input PDF -> output folder. Each input PDF is always saved with cleanup
and embedded-image compression (garbage collection, deflate, deflate images
and fonts). When "Compress embedded images" is enabled, every embedded image
whose effective resolution exceeds the configured maximum is downsampled via
Pillow (LANCZOS) to the target pixel size, re-encoded in its original format
(png keeps transparency, jpg uses the given quality), and replaced in place --
but only if the re-encoded bytes are smaller than the original. Images in other
formats are skipped so the original format is preserved.

Progress granularity:
  * without "Compress embedded images": counted per file
  * with    "Compress embedded images": counted per page (processed page by page)

A single failed file is skipped and counted into the summary.
"""

import io

import pymupdf
from multiprocessing import Process, Queue, Event
from pathlib import Path
from queue import Empty
from tkinter.messagebox import showerror, showinfo
from typing import Any, Dict

from util.i18n import gettext_text as _


def _downscale_page_images(
    doc, page, max_dpi: int, jpg_quality: int, ctr: Dict[str, int]
) -> None:
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


def worker(
    params: Dict[str, Any], progress_queue: Queue, cancel_event: Event
) -> None:
    """Compress every input PDF into the output folder.

    Messages put on ``progress_queue`` are tuples:
        ('progress', current, total, message)
        ('done', summary)
        ('error', message)
        ('cancelled', None)
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']
    compress_images = options['compress_images']
    max_dpi = options['max_dpi']
    jpg_quality = options['jpg_quality']

    try:
        total = len(inputs)
        if total == 0:
            progress_queue.put(('error', _('No input files.')))
            return

        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        files_done = 0
        files_failed = 0
        ctr = {'downscaled': 0, 'skipped_bigger': 0, 'skipped_format': 0}

        if compress_images:
            # pre-count total pages for the progress denominator
            total_pages = 0
            for in_path in inputs:
                try:
                    d = pymupdf.open(str(in_path))
                    total_pages += d.page_count
                    d.close()
                except Exception:
                    pass

            page_index = 0
            for in_path in inputs:
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return
                src = Path(in_path)
                try:
                    doc = pymupdf.open(str(src))
                    try:
                        for p_idx in range(doc.page_count):
                            if cancel_event.is_set():
                                progress_queue.put(('cancelled', None))
                                doc.close()
                                return
                            page = doc[p_idx]
                            page_index += 1
                            progress_queue.put(
                                ('progress', page_index, total_pages,
                                 _('Compressing images…… %s (%d/%d)')
                                 % (src.name, page_index, total_pages))
                            )
                            _downscale_page_images(
                                doc, page, max_dpi, jpg_quality, ctr
                            )
                        out_file = out_dir / f'{src.stem}.{_("Compress")}.pdf'
                        doc.save(
                            str(out_file), garbage=4, clean=True,
                            deflate=True, deflate_images=True, deflate_fonts=True,
                        )
                        files_done += 1
                    finally:
                        doc.close()
                except Exception as exc:
                    files_failed += 1
                    progress_queue.put(
                        ('progress', page_index, total_pages,
                         _('Failed: %s (%s: %s)')
                         % (src.name, type(exc).__name__, exc))
                    )
        else:
            for index, in_path in enumerate(inputs, start=1):
                if cancel_event.is_set():
                    progress_queue.put(('cancelled', None))
                    return
                src = Path(in_path)
                progress_queue.put(
                    ('progress', index, total,
                     _('Compressing…… %d/%d') % (index, total))
                )
                try:
                    doc = pymupdf.open(str(src))
                    try:
                        out_file = out_dir / f'{src.stem}.{_("Compress")}.pdf'
                        doc.save(
                            str(out_file), garbage=4, clean=True,
                            deflate=True, deflate_images=True, deflate_fonts=True,
                        )
                        files_done += 1
                    finally:
                        doc.close()
                except Exception as exc:
                    files_failed += 1
                    progress_queue.put(
                        ('progress', index, total,
                         _('Failed: %s (%s: %s)')
                         % (src.name, type(exc).__name__, exc))
                    )

        summary = _('Compressed %d file(s).') % files_done
        if compress_images:
            summary += ' ' + (_('Downscaled %d image(s).') % ctr['downscaled'])
            if ctr['skipped_bigger']:
                summary += ' ' + (
                    _('%d image(s) kept (new size not smaller).')
                    % ctr['skipped_bigger']
                )
            if ctr['skipped_format']:
                summary += ' ' + (
                    _('%d image(s) skipped (unsupported format).')
                    % ctr['skipped_format']
                )
        if files_failed:
            summary += ' ' + (_('%d file(s) failed.') % files_failed)
        if files_done == 0 and total > 0:
            progress_queue.put(('error', summary))
            return

        done_pages = total_pages if compress_images else total
        progress_queue.put(('progress', done_pages, done_pages, _('Done')))
        progress_queue.put(('done', summary))

    except Exception as exc:
        progress_queue.put(('error', '%s: %s' % (type(exc).__name__, exc)))


def run_compress_pdf_with_progress(master, params: Dict[str, Any]) -> None:
    """Run PDF compression in a subprocess and show progress via ProgressDialog."""
    from core.progress_dialog import ProgressDialog

    progress_queue: Queue = Queue()
    cancel_event: Event = Event()
    process = None
    finished = False

    def _on_cancel():
        nonlocal finished
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

    dialog = ProgressDialog(
        master,
        title=_('Compress PDF'),
        label_text=_('Preparing...'),
        cancel_command=_on_cancel,
        mode='determinate',
    )

    process = Process(target=worker, args=(params, progress_queue, cancel_event))
    process.start()
    master.after(100, _poll)
