# toolkit/core/image_to_pdf_worker.py

from pathlib import Path

import pymupdf  # 导入 PyMuPDF

from toolkit.i18n import gettext_text as _
from toolkit.i18n import ngettext


def image_to_pdf_worker(
    image_files,
    output_pdf_path,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        total_steps = len(image_files)
        progress_queue.put(("INIT", total_steps))

        with pymupdf.open() as output_doc:
            for i, image_file in enumerate(image_files):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return

                if not Path(image_file).exists():
                    progress_queue.put(("PROGRESS", i + 1))
                    continue

                try:
                    with pymupdf.open(image_file) as img_doc:
                        pdf_bytes = img_doc.convert_to_pdf()
                        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf_doc:
                            output_doc.insert_pdf(pdf_doc)
                except Exception as img_e:
                    print(f"Error converting image {image_file}: {img_e}")
                    result_queue.put(
                        (
                            "ERROR",
                            _("Error converting image {}:\n{}").format(
                                Path(image_file).name, img_e
                            ),
                        )
                    )
                    return

                progress_queue.put(("PROGRESS", i + 1))

            if not output_doc.page_count:
                raise ValueError(_("No image converted to PDF."))

            progress_queue.put(("SAVING", _("Saving PDF...")))
            # Wait for UI thread to confirm SAVING message processed,
            # while periodically checking the cancel event.
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                # Wait briefly, then check the cancel event again
                saving_ack_event.wait(timeout=0.1)
            output_doc.save(output_pdf_path, garbage=4, deflate=True)

        success_msg = ngettext(
            "Converted {} image into PDF.", "Converted {} images into PDF.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
