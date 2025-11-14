from pathlib import Path
from typing import Any, List
from functools import lru_cache

import pymupdf

from toolkit.i18n import gettext_text as _
from toolkit.i18n import ngettext
from toolkit.util.page_range_parser import parse_page_ranges


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
        return parse_page_ranges(str(split_value), total_pages, allow_duplicates=True)

    else:
        raise ValueError(
            _("Unknown split mode: {split_mode}").format(split_mode=split_mode)
        )


@lru_cache(maxsize=10)
def get_pdf_bytes_cached(pdf_path_str):
    """Get the byte content of the PDF, and return directly if it is cached."""
    with pymupdf.open(pdf_path_str) as doc:
        return doc.tobytes()


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

        with pymupdf.open(pdf_path_obj) as src_doc:
            total_pages = len(src_doc)
            if total_pages == 0:
                raise ValueError(_("PDF file is empty, no pages to split."))

            page_chunks = _get_page_chunks(total_pages, split_mode, split_value)
            total_files_to_create = len(page_chunks)
            progress_queue.put(("INIT", total_files_to_create))

            output_folder_obj.mkdir(parents=True, exist_ok=True)
            base_filename = pdf_path_obj.stem
            
            if total_files_to_create == 1:
                # Single file output - create file directly in the same directory as the input file
                if split_mode == "custom_ranges":
                    # Name by range, "R{range_str}.pdf", "," is replaced by "_", ":" is replaced by "s"
                    range_str = split_value  # Use original split_value
                    safe_range_str = range_str.replace(",", "_").replace(":", "s")
                    output_name = f"{base_filename}_R{safe_range_str}.pdf"
                elif split_mode in ["fixed_pages", "fixed_files"]:
                    # Name by number of pages/files, "P{start_page_number}-{end_page_number}.pdf"
                    page_list = page_chunks[0]
                    start_page = page_list[0] + 1
                    end_page = page_list[-1] + 1
                    output_name = f"{base_filename}_P{start_page}-{end_page}.pdf"
                else:  # "single_page"
                    # Name for single page split, "P{page_number}.pdf"
                    page_list = page_chunks[0]
                    page_num = page_list[0] + 1
                    output_name = f"{base_filename}_P{page_num}.pdf"
                    
                output_path = output_folder_obj / output_name

                # Handle single file output
                with pymupdf.open(stream=get_pdf_bytes_cached(str(pdf_path_obj)), filetype="pdf") as temp_doc:
                    temp_doc.select(page_chunks[0])  # Keep required pages
                    temp_doc.save(str(output_path), garbage=3, deflate=True)

                progress_queue.put(("PROGRESS", 1))
            else:
                # Multi-file output - create a subfolder named after the input file without extension
                subfolder_name = f"{base_filename}_{_('Split')}"
                subfolder_path = output_folder_obj / subfolder_name
                subfolder_path.mkdir(parents=True, exist_ok=True)
                
                for i, page_list in enumerate(page_chunks):
                    if cancel_event.is_set():
                        result_queue.put(("CANCEL", _("Cancelled by user.")))
                        return

                    with pymupdf.open(stream=get_pdf_bytes_cached(str(pdf_path_obj)), filetype="pdf") as temp_doc:
                        temp_doc.select(page_list)  # Keep required pages

                        if split_mode == "custom_ranges":
                            # Name by range, "R{range_str}.pdf", "," is replaced by "_", ":" is replaced by "s"
                            # Generate range description for each chunk separately
                            range_parts = []
                            start_idx = 0
                            while start_idx < len(page_list):
                                # Find consecutive page segments
                                end_idx = start_idx
                                while end_idx < len(page_list) - 1 and page_list[end_idx] + 1 == page_list[end_idx + 1]:
                                    end_idx += 1

                                if start_idx == end_idx:
                                    # Single page
                                    range_parts.append(f"P{page_list[start_idx] + 1}")
                                else:
                                    # Page range
                                    range_parts.append(f"P{page_list[start_idx] + 1}-{page_list[end_idx] + 1}")

                                start_idx = end_idx + 1

                            range_str = "_".join(range_parts)
                            # Replace comma with '_' and colon with 's' in the output filename
                            range_str = range_str.replace(",", "_").replace(":", "s")
                            output_name = f"R{range_str}.pdf"
                        elif split_mode in ["fixed_pages", "fixed_files"]:
                            # Name by number of pages/files, "P{start_page_number}-{end_page_number}.pdf"
                            start_page = page_list[0] + 1
                            end_page = page_list[-1] + 1
                            output_name = f"P{start_page}-{end_page}.pdf"
                        else:  # "single_page"
                            # Name for single page split, "P{page_number}.pdf"
                            page_num = page_list[0] + 1
                            output_name = f"P{page_num}.pdf"

                        output_path = subfolder_path / output_name
                        temp_doc.save(str(output_path), garbage=3, deflate=True)

                    progress_queue.put(("PROGRESS", i + 1))

        success_msg = ngettext(
            "Split into {} PDF file.", "Split into {} PDF files.", total_files_to_create
        ).format(total_files_to_create)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))