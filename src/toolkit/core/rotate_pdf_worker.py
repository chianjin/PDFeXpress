# toolkit/core/rotate_pdf_worker.py

from pathlib import Path

from pikepdf import Pdf

from toolkit.i18n import gettext_text as _, ngettext


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

            with Pdf.open(file_path) as pdf:
                for page in pdf.pages:
                    # Use relative rotation to add the rotation angle to the current rotation
                    page.rotate(rotation_angle, relative=True)

                p = Path(file_path)
                new_stem = f"{p.stem}_{_("Rotate")}{rotation_angle}"
                if save_to_same_folder:
                    output_path = p.with_name(f"{new_stem}{p.suffix}")
                else:
                    output_path = Path(output_dir) / f"{new_stem}{p.suffix}"

                # Save using context manager
                with pdf:
                    pdf.save(output_path)

            progress_queue.put(("PROGRESS", i + 1))

        success_msg = ngettext(
            "Rotated {} PDF file.", "Rotated {} PDF files.", total_steps
        ).format(total_steps)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
