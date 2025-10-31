# toolkit/core/merge_pdf_worker.py

import pymupdf
from pathlib import Path

from toolkit.i18n import gettext_text as _, gettext_plural as _n


def pdf_merge_worker(input_files, output_file, create_bookmarks,
                    cancel_event, progress_queue, result_queue):
    try:
        total_steps = len(input_files)
        progress_queue.put(("INIT", total_steps))

        with pymupdf.open() as output_doc:
            # 用于存储书签信息的列表
            toc = []
            current_page = 0
            
            for i, file_path in enumerate(input_files):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Task cancelled by user.")))
                    return
                with pymupdf.open(file_path) as input_doc:
                    if create_bookmarks:
                        # 获取不带扩展名的文件名作为书签条目
                        bookmark_title = Path(file_path).stem
                        # 添加书签，指向当前文档的第一页
                        toc.append([1, bookmark_title, current_page + 1])  # [level, title, page]
                    output_doc.insert_pdf(input_doc)
                    current_page += input_doc.page_count
                progress_queue.put(("PROGRESS", i + 1))
            
            # 设置整个文档的目录
            if create_bookmarks and toc:
                output_doc.set_toc(toc)
                
            output_doc.save(output_file, garbage=4, deflate=True)

        success_msg = _n(
            "Successfully merged {} file!",
            "Successfully merged {} files!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg + "\n" + _("Saved to:") + f" {output_file}"))

    except Exception as e:
        result_queue.put(("ERROR", _("An unexpected error occurred:\n{}").format(e)))
