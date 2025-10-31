# toolkit/core/image_to_pdf_worker.py
import os
import fitz # 导入 PyMuPDF

from toolkit.i18n import gettext_text as _, gettext_plural as _n

def image_to_pdf_worker(image_files, output_pdf_path, cancel_event, progress_queue, result_queue):
    """业务逻辑: 图像转 PDF。"""
    print(f"[工作进程 {os.getpid()}]: 开始图像转 PDF...")
    try:
        if not image_files:
            raise ValueError(_("No image files selected for conversion."))
        
        total_steps = len(image_files)
        progress_queue.put(("INIT", total_steps))

        with fitz.open() as output_doc: # 创建一个新的 PDF 文档用于输出
            for i, image_file in enumerate(image_files):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Task cancelled by user.")))
                    return
                
                if not os.path.exists(image_file):
                    print(f"Warning: Image file not found: {image_file}")
                    progress_queue.put(("PROGRESS", i + 1)) # 即使文件不存在也更新进度
                    continue

                try:
                    # 打开图像文件
                    img_doc = fitz.open(image_file)
                    # 将图像转换为 PDF 字节流
                    pdf_bytes = img_doc.convert_to_pdf()
                    # 以 PDF 格式打开字节流
                    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    # 插入到输出 PDF 文档中
                    output_doc.insert_pdf(pdf_doc)
                    # 关闭临时 PDF 文档
                    pdf_doc.close()
                    img_doc.close()
                except Exception as img_e:
                    print(f"Error converting image {image_file}: {img_e}")
                    result_queue.put(("ERROR", _("Error converting image {}:\n{}").format(os.path.basename(image_file), img_e)))
                    return
                
                progress_queue.put(("PROGRESS", i + 1))
            
            if not output_doc.page_count:
                raise ValueError(_("No images were successfully converted to PDF."))

            output_doc.save(output_pdf_path, garbage=4, deflate=True)

        success_msg = _n(
            "Successfully converted {} image to PDF!",
            "Successfully converted {} images to PDF!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg + f"\n" + _("Saved to:") + f" {output_pdf_path}"))

    except Exception as e:
        result_queue.put(("ERROR", _("An unexpected error occurred:\n{}").format(e)))
