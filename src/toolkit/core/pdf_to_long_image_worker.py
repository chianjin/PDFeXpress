# toolkit/core/pdf_to_long_image_worker.py

import pymupdf
from PIL import Image

from toolkit.i18n import gettext_text as _


def pdf_to_long_image_worker(
        pdf_path,
        output_image_path,
        dpi_value,
        cancel_event,
        progress_queue,
        result_queue,
        saving_ack_event
):
    try:
        with pymupdf.open(pdf_path) as doc:
            total_pages = len(doc)
            if total_pages == 0:
                raise ValueError(_("PDF file has no pages."))

            progress_queue.put(("INIT", total_pages + 1))  # +1 for the final stitching step

            page_images = []
            total_width = 0
            total_height = 0

            for i in range(total_pages):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return

                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=dpi_value)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                page_images.append(img)
                total_width = max(total_width, img.width)
                total_height += img.height
                progress_queue.put(("PROGRESS", i + 1))

            if not page_images:
                raise ValueError(_("No pages were rendered from the PDF."))

            long_image = Image.new('RGB', (total_width, total_height), (255, 255, 255))
            current_y = 0
            for img in page_images:
                long_image.paste(img, (0, current_y))
                current_y += img.height

            progress_queue.put(("SAVING", _("Saving long image...")))
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                saving_ack_event.wait(timeout=0.1)

            long_image.save(output_image_path)
            progress_queue.put(("PROGRESS", total_pages + 1))

        success_msg = _("PDF converted to a long image.")
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred:\n{}").format(e)))
