# toolkit/core/rotate_pdf_worker.py

from pathlib import Path

import pymupdf

from toolkit.i18n import gettext_text as _
from toolkit.i18n import ngettext


def pdf_rotate_worker(
    input_files,
    output_dir,
    rotation_angle,
    save_to_same_folder,
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

            with pymupdf.open(file_path) as doc:
                for page in doc:
                    current_rotation = page.rotation
                    new_rotation = (current_rotation + rotation_angle) % 360
                    page.set_rotation(new_rotation)

                p = Path(file_path)
                if save_to_same_folder:
                    new_stem = f"{p.stem}_{_('Rotated')}_{rotation_angle}"
                    output_path = p.with_name(f"{new_stem}{p.suffix}")
                else:
                    output_path = Path(output_dir) / p.name

                doc.save(str(output_path), garbage=4, deflate=True)

            progress_queue.put(("PROGRESS", i + 1))

        success_msg = ngettext(
            "Rotated {} PDF file.", "Rotated {} PDF files.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
