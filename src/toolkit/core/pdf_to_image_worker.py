# toolkit/core/pdf_to_image_worker.py
from pathlib import Path

import pymupdf

from toolkit.i18n import gettext_text as _, ngettext


def pdf_to_image_worker(
        input_files,
        output_dir,
        dpi_value,
        image_format,
        jpeg_quality,
        transparent_background,
        save_in_same_folder,
        cancel_event,
        progress_queue,
        result_queue,
        saving_ack_event
):
    try:
        total_steps = 0
        for file_path in input_files:
            with pymupdf.open(file_path) as doc:
                total_steps += doc.page_count
        progress_queue.put(("INIT", total_steps))

        current_step = 0
        for file_path in input_files:
            if cancel_event.is_set():
                result_queue.put(("CANCEL", _("Cancelled by user.")))
                return

            pdf_path_obj = Path(file_path)
            pdf_name_only = pdf_path_obj.stem

            if save_in_same_folder:
                sub_output_dir = pdf_path_obj.parent / pdf_name_only
            else:
                sub_output_dir = Path(output_dir) / pdf_name_only

            sub_output_dir.mkdir(parents=True, exist_ok=True)

            with pymupdf.open(file_path) as doc:
                pdf_path_obj = Path(file_path)
                pdf_name_only = pdf_path_obj.stem

                # Calculate padding for page numbers
                num_digits = len(str(doc.page_count))

                for i in range(doc.page_count):
                    if cancel_event.is_set():
                        result_queue.put(("CANCEL", _("Cancelled by user.")))
                        return

                    page = doc.load_page(i)
                    pix = page.get_pixmap(dpi=dpi_value, alpha=transparent_background)

                    # Zero-pad the page number
                    page_num_str = str(i + 1).zfill(num_digits)
                    new_filename = f"{pdf_name_only}_page_{page_num_str}.{image_format}"
                    output_filename = sub_output_dir / new_filename

                    if image_format == 'jpg':
                        pix.save(str(output_filename), jpg_quality=jpeg_quality)
                    else:
                        pix.save(str(output_filename))

                    current_step += 1
                    progress_queue.put(("PROGRESS", current_step))

        success_msg = ngettext(
            "{} page converted!",
            "{} pages converted!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred:\n{}").format(e)))
