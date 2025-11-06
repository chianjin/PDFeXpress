# toolkit/core/merge_pdf_worker.py

from pathlib import Path
from pikepdf import Pdf, OutlineItem

from toolkit.i18n import gettext_text as _, ngettext

translation_table = str.maketrans("-_.,", "    ")


def replace_special_chars(text):
    return text.translate(translation_table)


def _add_bookmarks_to_pdf(pdf, input_files, bookmark_positions):
    """
    添加书签到pdf
    bookmark_positions: 一个列表，包含每个需要书签的PDF的位置信息
    """
    if not bookmark_positions:
        return

    with pdf.open_outline() as outline:
        for file_path, start_page_idx in bookmark_positions:
            bookmark_title = replace_special_chars(Path(file_path).stem)
            
            # 确保页码索引在范围内
            target_page_idx = min(start_page_idx, len(pdf.pages) - 1)
            
            # 创建书签项并添加到根节点
            outline_item = OutlineItem(bookmark_title, target_page_idx)
            outline.root.append(outline_item)


def merge_pdf_worker(
    input_files,
    output_file,
    create_bookmarks,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):  # 添加 saving_ack_event
    try:
        total_steps = len(input_files)
        progress_queue.put(("INIT", total_steps))

        with Pdf.new() as output_pdf:
            # list for bookmark entries
            bookmark_positions = []
            current_page = 0

            for i, file_path in enumerate(input_files):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                    
                with Pdf.open(file_path) as input_pdf:
                    if create_bookmarks:
                        # 记录需要添加书签的位置
                        bookmark_positions.append((file_path, current_page))
                    
                    # Append all pages from input PDF to output PDF
                    for page in input_pdf.pages:
                        output_pdf.pages.append(page)
                    
                    current_page += len(input_pdf.pages)
                progress_queue.put(("PROGRESS", i + 1))

            # 如果需要创建书签，则添加书签
            if create_bookmarks and bookmark_positions:
                _add_bookmarks_to_pdf(output_pdf, input_files, bookmark_positions)

            progress_queue.put(("SAVING", _("Saving merged PDF...")))
            # Wait for UI thread to confirm SAVING message processed,
            # while periodically checking the cancel event.
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                # Wait briefly, then check the cancel event again
                saving_ack_event.wait(timeout=0.1)
            
            output_pdf.save(output_file)

        success_msg = ngettext(
            "Merged {} PDF file.", "Merged {} PDF files.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
