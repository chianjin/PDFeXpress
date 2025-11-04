# toolkit/core/extract_images_worker.py

from pathlib import Path

import pymupdf

from toolkit.i18n import gettext_text as _


def extract_images_worker(
    input_files,
    output_dir,
    min_width,
    min_height,
    save_in_same_folder,
    extract_all,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event=None,
):
    try:
        total_images_found = 0
        images_extracted_count = 0

        for file_path in input_files:
            with pymupdf.open(file_path) as doc:
                total_images_found += sum(
                    len(page.get_images(full=True)) for page in doc
                )

        progress_queue.put(("INIT", total_images_found))

        for file_path in input_files:
            if cancel_event.is_set():
                result_queue.put(("CANCEL", _("Cancelled by user.")))
                return

            pdf_path_obj = Path(file_path)
            if save_in_same_folder:
                output_subfolder = pdf_path_obj.parent / pdf_path_obj.stem
            else:
                output_subfolder = Path(output_dir) / pdf_path_obj.stem
            output_subfolder.mkdir(parents=True, exist_ok=True)

            with pymupdf.open(file_path) as doc:
                for page_num, page in enumerate(doc):
                    img_list = page.get_images(full=True)
                    for img_info in img_list:
                        xref = img_info[0]
                        w = img_info[2]
                        h = img_info[3]

                        if extract_all or (w >= min_width and h >= min_height):
                            img_dict = doc.extract_image(xref)
                            if not img_dict:
                                continue

                            img_bytes = img_dict["image"]
                            img_ext = img_dict["ext"]

                            img_filename = (
                                f"{pdf_path_obj.stem}_p{page_num + 1}_{xref}.{img_ext}"
                            )
                            img_path = output_subfolder / img_filename
                            img_path.write_bytes(img_bytes)
                            images_extracted_count += 1

                        progress_queue.put(("PROGRESS", images_extracted_count))

        success_msg = _("Found {} images, extracted {} images.").format(
            total_images_found, images_extracted_count
        )
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
