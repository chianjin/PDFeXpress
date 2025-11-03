# toolkit/core/interleave_pdf_worker.py

import pymupdf

from toolkit.i18n import gettext_text as _


def interleave_pdf_worker(
        pdf_path_a,
        pdf_path_b,
        output_pdf_path,
        reverse_b,
        cancel_event,
        progress_queue,
        result_queue,
        saving_ack_event
):
    try:
        with pymupdf.open(pdf_path_a) as doc_a, pymupdf.open(pdf_path_b) as doc_b, pymupdf.open() as new_doc:
            len_a = len(doc_a)
            len_b = len(doc_b)
            total_pages_to_insert = len_a + len_b
            progress_queue.put(("INIT", total_pages_to_insert))

            if total_pages_to_insert == 0:
                raise ValueError(_("Input files are empty, no pages to merge."))

            max_len = max(len_a, len_b)
            pages_processed = 0

            for i in range(max_len):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return

                if i < len_a:
                    new_doc.insert_pdf(doc_a, from_page=i, to_page=i)
                    pages_processed += 1

                if i < len_b:
                    page_b_index = (len_b - 1) - i if reverse_b else i
                    new_doc.insert_pdf(doc_b, from_page=page_b_index, to_page=page_b_index)
                    pages_processed += 1

                progress_queue.put(("PROGRESS", pages_processed))

            progress_queue.put(("SAVING", _("Saving PDF...")))
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                saving_ack_event.wait(timeout=0.1)

            new_doc.save(output_pdf_path, garbage=4, deflate=True)

        success_msg = _("PDF interleaved.")
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred:\n{}").format(e)))
