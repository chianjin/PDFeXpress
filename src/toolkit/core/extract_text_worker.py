# toolkit/core/extract_text_worker.py
from pathlib import Path

import pymupdf

from toolkit.i18n import gettext_text as _, ngettext


def extract_text_worker(
        input_files,
        output_dir,
        sort_text,
        save_in_same_folder,
        cancel_event,
        progress_queue,
        result_queue,
        saving_ack_event
):
    try:
        total_steps = len(input_files)
        progress_queue.put(("INIT", total_steps))

        for i, file_path in enumerate(input_files):
            if cancel_event.is_set():
                result_queue.put(("CANCEL", _("Cancelled by user.")))
                return

            with pymupdf.open(file_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text(sort=sort_text)

                pdf_path_obj = Path(file_path)
                if save_in_same_folder:
                    output_path = pdf_path_obj.parent / f"{pdf_path_obj.stem}.txt"
                else:
                    output_path = Path(output_dir) / f"{pdf_path_obj.stem}.txt"
                output_path.write_text(text, encoding='utf-8')

            progress_queue.put(("PROGRESS", i + 1))

        success_msg = ngettext(
            "Extracted text from {} file.",
            "Extracted text from {} files.",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred:\n{}").format(e)))
