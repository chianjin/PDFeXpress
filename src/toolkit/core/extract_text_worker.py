# toolkit/core/extract_text_worker.py

from pathlib import Path
from pypdfium2 import PdfDocument

from toolkit.i18n import gettext_text as _, ngettext


def extract_text_worker(
    input_files,
    output_dir,
    add_page_separator,
    save_in_same_folder,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        total_steps = len(input_files)
        progress_queue.put(("INIT", total_steps))

        for i, file_path in enumerate(input_files):
            if cancel_event.is_set():
                result_queue.put(("CANCEL", _("Cancelled by user.")))
                return

            # pypdfium2 doesn't have a direct sort option like PyMuPDF
            # We'll extract text from each page
            with PdfDocument(file_path) as doc:
                text_parts = []
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text_page = page.get_textpage()
                    page_text = text_page.get_text_range()
                    # Normalize line endings to \n and clean up
                    page_text = page_text.replace('\r\n', '\n').replace('\r', '\n')
                    # Split into lines and remove empty lines
                    lines = [line for line in page_text.split('\n') if line.strip()]
                    page_text = '\n'.join(lines)
                    text_parts.append(page_text)
                    # Add a page separator if option is enabled
                    if add_page_separator:
                        text_parts.append(f"{'='*25} {_('PAGE {} END').format(page_num+1)} {'='*25}"
)

                text = '\n'.join(text_parts)

            pdf_path_obj = Path(file_path)
            if save_in_same_folder:
                output_path = pdf_path_obj.parent / f"{pdf_path_obj.stem}.txt"
            else:
                output_path = Path(output_dir) / f"{pdf_path_obj.stem}.txt"
            
            # Normalize line endings to platform default
            import os
            text = text.replace('\n', os.linesep).replace('\r', '')
            
            output_path.write_text(text, encoding="utf-8")

            progress_queue.put(("PROGRESS", i + 1))

        success_msg = ngettext(
            "Extracted text from {} file.", "Extracted text from {} files.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
