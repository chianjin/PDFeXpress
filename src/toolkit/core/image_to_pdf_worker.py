# toolkit/core/image_to_pdf_worker.py
import os
from pathlib import Path
import pymupdf # 导入 PyMuPDF

from toolkit.i18n import gettext_text as _, gettext_plural as _n

def image_to_pdf_worker(image_files, output_pdf_path, cancel_event, progress_queue, result_queue, saving_ack_event): # 添加 saving_ack_event
    """业务逻辑: 图像转 PDF。"""
    print(f"[工作进程 {os.getpid()}]: 开始图像转 PDF...")
    try:
        total_steps = len(image_files)
        progress_queue.put(("INIT", total_steps))

        with pymupdf.open() as output_doc: # 创建一个新的 PDF 文档用于输出
            for i, image_file in enumerate(image_files):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Task cancelled by user.")))
                    return
                
                if not Path(image_file).exists():
                    print(f"Warning: Image file not found: {image_file}")
                    progress_queue.put(("PROGRESS", i + 1)) # 即使文件不存在也更新进度
                    continue

                try:
                    # 打开图像文件
                    with pymupdf.open(image_file) as img_doc:
                        # 将图像转换为 PDF 字节流
                        pdf_bytes = img_doc.convert_to_pdf()
                        # 以 PDF 格式打开字节流
                        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf_doc:
                            # 插入到输出 PDF 文档中
                            output_doc.insert_pdf(pdf_doc)
                except Exception as img_e:
                    print(f"Error converting image {image_file}: {img_e}")
                    result_queue.put(("ERROR", _("Error converting image {}:\n{}").format(Path(image_file).name, img_e)))
                    return
                
                progress_queue.put(("PROGRESS", i + 1))
            
            if not output_doc.page_count:
                raise ValueError(_("No images were successfully converted to PDF."))

            progress_queue.put(("SAVING", _("Saving PDF...")))
            # 等待 UI 线程确认 SAVING 消息已处理，同时定期检查取消事件
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Task cancelled by user.")))
                    return
                saving_ack_event.wait(timeout=0.1) # 短暂等待，然后再次检查取消事件
            output_doc.save(output_pdf_path, garbage=4, deflate=True)

        success_msg = _n(
            "Successfully converted {} image to PDF!",
            "Successfully converted {} images to PDF!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg + "\n" + _("Saved to:") + f" {output_pdf_path}"))

    except Exception as e:
        result_queue.put(("ERROR", _("An unexpected error occurred:\n{}").format(e)))
