# toolkit/core/extract_images_worker.py

from pathlib import Path

from pikepdf import Pdf, PdfImage

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

        # Count total images in all files first (to initialize progress)
        for file_path in input_files:
            with Pdf.open(file_path) as pdf:
                xref_list = []  # Track xrefs to skip duplicates
                for page in pdf.pages:
                    for img_name in page.images.keys():
                        xref = page.images[img_name].objgen
                        if xref in xref_list:
                            continue  # Skip duplicate image
                        xref_list.append(xref)
                        total_images_found += 1


        progress_queue.put(("INIT", total_images_found))

        images_extracted_count = 0
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

            with Pdf.open(file_path) as pdf:
                xref_list = []  # Track xrefs to skip duplicates
                for page_num, page in enumerate(pdf.pages, start=1):
                    # 使用 page.images 获取页面中的所有图像
                    for img_name in page.images.keys():
                        xref = page.images[img_name].objgen
                        if xref in xref_list:
                            continue  # Skip duplicate image
                        xref_list.append(xref)
                        try:
                            # 尝试将对象解析为图像
                            pdf_img = PdfImage(page.images[img_name])
                        except Exception as e:
                            continue  # Skip non-image XObject

                        # 检查是否满足尺寸要求
                        if extract_all or (pdf_img.width >= min_width and pdf_img.height >= min_height):
                            # 使用PikePDF的extract_to方法，它会自动处理扩展名
                            img_prefix = output_subfolder / f"P{page_num:02d}_{img_name[1:]}"
                            img_path = pdf_img.extract_to(fileprefix=img_prefix)
                            images_extracted_count += 1

                        progress_queue.put(("PROGRESS", images_extracted_count))

        success_msg = _("Found {} images, extracted {} images.").format(
            total_images_found, images_extracted_count
        )
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
