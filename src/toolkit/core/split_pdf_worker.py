# toolkit/core/split_pdf_worker.py

from pathlib import Path
from typing import Any, List

from pikepdf import Pdf

from toolkit.i18n import gettext_text as _
from toolkit.i18n import ngettext


def _parse_page_ranges(range_string: str, total_pages: int) -> List[List[int]]:
    chunks: List[List[int]] = []
    if not range_string:
        raise ValueError(_("Custom range string cannot be empty."))
    parts: List[str] = range_string.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            chunk: List[int]
            if "-" in part:
                start_str, end_str = part.split("-", 1)
                start: int = int(start_str.strip())
                end: int = int(end_str.strip())
                if start < 1 or end > total_pages or start > end:
                    raise ValueError(
                        _(
                            "Invalid range '{part}': must be between 1-{total_pages}, and start <= end."
                        ).format(part=part, total_pages=total_pages)
                    )
                chunk = list(range(start - 1, end))
            else:
                page: int = int(part)
                if page < 1 or page > total_pages:
                    raise ValueError(
                        _(
                            "Invalid page '{part}': must be between 1-{total_pages}."
                        ).format(part=part, total_pages=total_pages)
                    )
                chunk = [page - 1]
            chunks.append(chunk)
        except Exception as e:
            raise ValueError(
                _("Invalid custom range '{part}' format: {e}").format(
                    part=part, e=str(e)
                )
            )
    return chunks


def _get_page_chunks(
    total_pages: int, split_mode: str, split_value: Any
) -> List[List[int]]:
    if split_mode == "single_page":
        return [[i] for i in range(total_pages)]

    elif split_mode == "fixed_pages":
        try:
            num = int(split_value)
            if num <= 0:
                raise ValueError(_("Value must be greater than 0"))
        except Exception:
            raise ValueError(
                _("Invalid pages per file value: {split_value}").format(
                    split_value=split_value
                )
            )

        return [
            list(range(i, min(i + num, total_pages)))
            for i in range(0, total_pages, num)
        ]

    elif split_mode == "fixed_files":
        try:
            num_files = int(split_value)
            if num_files <= 0:
                raise ValueError(_("Value must be greater than 0"))

            if num_files > total_pages:
                num_files = total_pages
        except Exception:
            raise ValueError(
                _("Invalid number of files value: {split_value}").format(
                    split_value=split_value
                )
            )

        base_pages, remainder = divmod(total_pages, num_files)
        chunks: List[List[int]] = []
        current_page = 0
        for i in range(num_files):
            pages_in_this_chunk = base_pages + (1 if i < remainder else 0)
            start, end = current_page, current_page + pages_in_this_chunk
            chunks.append(list(range(start, end)))
            current_page = end
        return chunks

    elif split_mode == "custom_ranges":
        return _parse_page_ranges(str(split_value), total_pages)

    else:
        raise ValueError(
            _("Unknown split mode: {split_mode}").format(split_mode=split_mode)
        )


def split_pdf_worker(
    pdf_path,
    output_dir,
    split_mode,
    split_value,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        pdf_path_obj = Path(pdf_path)
        output_folder_obj = Path(output_dir)

        with Pdf.open(pdf_path_obj) as src_pdf:
            total_pages = len(src_pdf.pages)
            if total_pages == 0:
                raise ValueError(_("PDF file is empty, no pages to split."))

            page_chunks = _get_page_chunks(total_pages, split_mode, split_value)
            total_files_to_create = len(page_chunks)
            progress_queue.put(("INIT", total_files_to_create))

            output_folder_obj.mkdir(parents=True, exist_ok=True)
            base_filename = pdf_path_obj.stem

            for i, page_list in enumerate(page_chunks):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return

                # Create output PDF inside the loop and use context manager to save it
                with Pdf.new() as output_pdf:
                    
                    # Add selected pages to the output PDF
                    for page_num in page_list:
                        output_pdf.pages.append(src_pdf.pages[page_num])

                    if split_mode == "custom_ranges":
                        range_name = (
                            f"p{page_list[0] + 1}"
                            if len(page_list) == 1
                            else f"p{page_list[0] + 1}-{page_list[-1] + 1}"
                        )
                        output_name = f"{base_filename}_{range_name}.pdf"
                    else:
                        output_name = f"{base_filename}_part_{i + 1:04d}.pdf"

                    output_path = output_folder_obj / output_name
                    
                    output_pdf.save(output_path)

                progress_queue.put(("PROGRESS", i + 1))

        success_msg = ngettext(
            "Split into {} PDF file.", "Split into {} PDF files.", total_files_to_create
        ).format(total_files_to_create)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
