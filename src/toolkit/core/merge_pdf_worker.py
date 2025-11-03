# toolkit/core/merge_pdf_worker.py

from pathlib import Path

import pymupdf

from toolkit.i18n import gettext_text as _, ngettext

translation_table = str.maketrans("-_.,", "    ")

def replace_special_chars(text):
    return text.translate(translation_table)

def merge_pdf_worker(input_files, output_file, create_bookmarks,
                     cancel_event, progress_queue, result_queue, saving_ack_event):  # 添加 saving_ack_event
    try:
        total_steps = len(input_files)
        progress_queue.put(("INIT", total_steps))

        with pymupdf.open() as output_doc:
            # list for bookmark entries
            toc = []
            current_page = 0

            for i, file_path in enumerate(input_files):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                with pymupdf.open(file_path) as input_doc:
                    if create_bookmarks:
                        # File name without extension as bookmark title
                        bookmark_title = replace_special_chars(Path(file_path).stem)
                        toc.append([1, bookmark_title, current_page + 1])  # [level, title, page]
                    output_doc.insert_pdf(input_doc)
                    current_page += input_doc.page_count
                progress_queue.put(("PROGRESS", i + 1))

            if create_bookmarks and toc:
                output_doc.set_toc(toc)

            progress_queue.put(("SAVING", _("Saving merged PDF...")))
            # Wait for UI thread to confirm SAVING message processed,
            # while periodically checking the cancel event.
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                # Wait briefly, then check the cancel event again
                saving_ack_event.wait(timeout=0.1)
            output_doc.save(output_file, garbage=4, deflate=True)

        success_msg = ngettext(
            "Merged {} file!",
            "Merged {} files!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred:\n{}").format(e)))
