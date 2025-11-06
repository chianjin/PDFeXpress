# toolkit/core/interleave_pdf_worker.py

from pikepdf import Pdf

from toolkit.i18n import gettext_text as _


def interleave_pdf_worker(
    pdf_path_a,
    pdf_path_b,
    output_pdf_path,
    reverse_b,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        with Pdf.open(pdf_path_a) as doc_a, Pdf.open(pdf_path_b) as doc_b:
            len_a = len(doc_a.pages)
            len_b = len(doc_b.pages)
            total_pages_to_insert = len_a + len_b
            progress_queue.put(("INIT", total_pages_to_insert))

            if total_pages_to_insert == 0:
                raise ValueError(_("Input files are empty, no pages to merge."))

            with Pdf.new() as output_pdf:
                max_len = max(len_a, len_b)
                pages_processed = 0

                for i in range(max_len):
                    if cancel_event.is_set():
                        result_queue.put(("CANCEL", _("Cancelled by user.")))
                        return

                    if i < len_a:
                        output_pdf.pages.append(doc_a.pages[i])
                        pages_processed += 1

                    if i < len_b:
                        page_b_index = (len_b - 1) - i if reverse_b else i
                        output_pdf.pages.append(doc_b.pages[page_b_index])
                        pages_processed += 1

                    progress_queue.put(("PROGRESS", pages_processed))

                progress_queue.put(("SAVING", _("Saving PDF...")))
                while not saving_ack_event.is_set():
                    if cancel_event.is_set():
                        result_queue.put(("CANCEL", _("Cancelled by user.")))
                        return
                    saving_ack_event.wait(timeout=0.1)

                output_pdf.save(output_pdf_path)

        success_msg = _("PDF interleaved.")
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
