# toolkit/core/merge_pdf_worker.py

import pymupdf

from toolkit.i18n import gettext_text as _, gettext_plural as _n


def pdf_merge_worker(input_files, output_file,
                    cancel_event, progress_queue, result_queue):
    try:
        total_steps = len(input_files)
        progress_queue.put(("INIT", total_steps))

        with pymupdf.open() as output_doc:
            for i, file_path in enumerate(input_files):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Task cancelled by user.")))
                    return
                with pymupdf.open(file_path) as input_doc:
                    output_doc.insert_pdf(input_doc)
                progress_queue.put(("PROGRESS", i + 1))
            output_doc.save(output_file, garbage=4, deflate=True)

        success_msg = _n(
            "Successfully merged {} file!",
            "Successfully merged {} files!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg + f"\n" + _("Saved to:") + f" {output_file}"))

    except Exception as e:
        result_queue.put(("ERROR", _("An unexpected error occurred:\n{}").format(e)))
