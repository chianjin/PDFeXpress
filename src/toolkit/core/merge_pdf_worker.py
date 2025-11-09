"""Worker module to merge multiple PDF files into one."""

from pathlib import Path
from typing import Any, List

import pymupdf
from toolkit.i18n import gettext_text as _
from toolkit.i18n import ngettext

translation_table = str.maketrans("-_.,", "    ")


def replace_special_chars(text: str) -> str:
    """Replace special characters in text with spaces."""
    return text.translate(translation_table)


def merge_pdf_worker(
    input_files: List[str],
    output_file: str,
    create_bookmarks: bool,
    duplex_printing: bool,
    cancel_event: Any,
    progress_queue: Any,
    result_queue: Any,
    saving_ack_event: Any,
) -> None:  # 添加 saving_ack_event
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
                        toc.append(
                            [1, bookmark_title, current_page + 1]
                        )  # [level, title, page]

                    output_doc.insert_pdf(input_doc)
                    current_page += input_doc.page_count

                    # Check if we need to add blank pages for duplex printing
                    if duplex_printing and input_doc.page_count % 2 != 0:
                        # If the current document has odd number of pages, add a blank page
                        output_doc.new_page()
                        current_page += 1
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
            "Merged {} PDF file.", "Merged {} PDF files.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
