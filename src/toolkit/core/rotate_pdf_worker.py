# toolkit/core/rotate_pdf_worker.py
from pathlib import Path

import pymupdf

from toolkit.i18n import gettext_text as _, gettext_plural as _n


def pdf_rotate_worker(
    input_files,
    output_dir,
    rotation_angle,
    save_to_same_folder,
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
                result_queue.put(("CANCEL", _("Task cancelled by user.")))
                return

            with pymupdf.open(file_path) as doc:
                for page in doc:
                    current_rotation = page.rotation
                    new_rotation = (current_rotation + rotation_angle) % 360
                    page.set_rotation(new_rotation)

                if save_to_same_folder:
                    output_path = Path(file_path).parent / f"{Path(file_path).stem}_rotated_{rotation_angle}.pdf"
                else:
                    output_path = Path(output_dir) / Path(file_path).name

                doc.save(str(output_path), garbage=4, deflate=True)

            progress_queue.put(("PROGRESS", i + 1))

        success_msg = _n(
            "Successfully rotated {} file!",
            "Successfully rotated {} files!",
            total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("An unexpected error occurred:\n{}").format(e)))
