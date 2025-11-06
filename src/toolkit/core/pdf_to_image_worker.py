# toolkit/core/pdf_to_image_worker.py

from pathlib import Path
from pypdfium2 import PdfDocument
from PIL import Image

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
    saving_ack_event,
):
    try:
        total_steps = 0
        for file_path in input_files:
            with PdfDocument(file_path) as doc:
                total_steps += len(doc)
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

            with PdfDocument(file_path) as doc:
                # Calculate padding for page numbers
                num_digits = len(str(len(doc)))

                for i in range(len(doc)):
                    if cancel_event.is_set():
                        result_queue.put(("CANCEL", _("Cancelled by user.")))
                        return

                    page = doc[i]
                    # Zero-pad the page number
                    page_num_str = str(i + 1).zfill(num_digits)
                    new_filename = f"{pdf_name_only}_page_{page_num_str}.{image_format}"
                    output_filename = sub_output_dir / new_filename

                    if image_format == 'png' and transparent_background:
                        pil_image = page.render(
                            scale=dpi_value / 72,
                            fill_color=(255, 255, 255, 0),
                            maybe_alpha=True
                        ).to_pil()
                        pil_image.save(str(output_filename), format='PNG', dpi=(dpi_value, dpi_value), optimize=True)
                    else:
                        pil_image = page.render(
                            scale=dpi_value / 72
                        ).to_pil()
                        # For JPG format
                        if image_format == 'jpg':
                            # Convert to RGB if necessary (JPEG doesn't support transparency)
                            if pil_image.mode in ('RGBA', 'LA', 'P'):
                                rgb_image = Image.new('RGB', pil_image.size, (255, 255, 255))
                                if pil_image.mode == 'RGBA':
                                    rgb_image.paste(pil_image, mask=pil_image.split()[-1])
                                else:
                                    rgb_image.paste(pil_image)
                                pil_image = rgb_image
                            pil_image.save(str(output_filename), format='JPEG', quality=jpeg_quality, dpi=(dpi_value, dpi_value), optimize=True)
                        else:  # For PNG format when transparent_background is False
                            pil_image.save(str(output_filename), format='PNG', dpi=(dpi_value, dpi_value), optimize=True)

                    current_step += 1
                    progress_queue.put(("PROGRESS", current_step))

        success_msg = ngettext(
            "Converted {} page to image.", "Converted {} pages to images.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
