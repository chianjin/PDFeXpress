# src/toolkit/core/pdf_to_image_worker.py
import os
from pathlib import Path
import pymupdf
from toolkit.i18n import gettext_text as _, gettext_plural as ngettext # 导入翻译函数

def pdf_to_image_worker(pdf_path, output_dir, dpi_value, image_format, cancel_event, progress_queue, result_queue):
    """业务逻辑 1: PDF 转图像。"""
    print(f"[工作进程 {os.getpid()}]: 开始 PDF转图像...")
    try:
        with pymupdf.open(pdf_path) as doc:
            if cancel_event.is_set():
                result_queue.put(("CANCEL", _("Task cancelled after opening file.")))
                return
            total_steps = doc.page_count
            if total_steps == 0: raise ValueError(_("PDF file has no pages."))
            progress_queue.put(("INIT", total_steps))

            pdf_path_obj = Path(pdf_path)
            pdf_basename = pdf_path_obj.name
            pdf_name_only = pdf_path_obj.stem
            has_alpha = (image_format == "png")

            for i in range(total_steps):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Task cancelled by user.")))
                    return 
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=dpi_value, alpha=has_alpha) 
                new_filename = f"{pdf_name_only}_page_{i+1}.{image_format}"
                output_filename = Path(output_dir) / new_filename
                pix.save(output_filename)
                progress_queue.put(("PROGRESS", i + 1))

        # 使用 ngettext 处理复数
        success_msg = ngettext(
            "Successfully converted {} page!",
            "Successfully converted {} pages!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("An unexpected error occurred:\n{}").format(e)))

