from pathlib import Path
from typing import List, Any

import pikepdf


def _parse_page_ranges(range_string: str, total_pages: int) -> List[List[int]]:
    """Parses a complex page range string into lists of 0-based page indices."""
    file_chunks_str = range_string.split(';')
    final_chunks = []

    for chunk_str in file_chunks_str:
        chunk_str = chunk_str.strip()
        if not chunk_str:
            continue

        allow_duplicates = chunk_str.startswith('+')
        if allow_duplicates:
            chunk_str = chunk_str[1:]

        current_file_pages = [] if allow_duplicates else set()
        parts = chunk_str.split(',')

        for part in parts:
            part = part.strip()
            if not part:
                continue

            step = 1
            if ':' in part:
                range_part, step_str = part.split(':', 1)
                step = int(step_str.strip())
            else:
                range_part = part

            if '-' in range_part:
                start_str, end_str = range_part.split('-', 1)
                start = int(start_str.strip()) if start_str.strip() else 1
                end = int(end_str.strip()) if end_str.strip() else total_pages
            else:
                if not range_part:
                    start = 1
                    end = total_pages
                else:
                    start = int(range_part.strip())
                    end = start

            if not (1 <= start <= end <= total_pages):
                raise ValueError(f"Invalid range '{part}': must be within 1-{total_pages}.")

            pages_for_part = range(start, end + 1, step)
            pages_to_add = [p - 1 for p in pages_for_part]

            if allow_duplicates:
                current_file_pages.extend(pages_to_add)
            else:
                current_file_pages.update(pages_to_add)

        if current_file_pages:
            if allow_duplicates:
                final_chunks.append(current_file_pages)
            else:
                final_chunks.append(sorted(list(current_file_pages)))

    return final_chunks


def _get_page_chunks(
    total_pages: int, split_mode: str, split_value: Any
) -> List[List[int]]:
    """Generates lists of page indices based on the selected split mode."""
    if split_mode == "single_page":
        return [[i] for i in range(total_pages)]

    elif split_mode == "fixed_pages":
        try:
            num = int(split_value)
            if num <= 0:
                raise ValueError("Value must be greater than 0")
        except Exception as e:
            raise ValueError(f"Invalid pages per file value: {split_value}: {e}")

        return [
            list(range(i, min(i + num, total_pages)))
            for i in range(0, total_pages, num)
        ]

    elif split_mode == "fixed_files":
        try:
            num_files = int(split_value)
            if num_files <= 0:
                raise ValueError("Value must be greater than 0")
            if num_files > total_pages:
                num_files = total_pages
        except Exception as e:
            raise ValueError(f"Invalid number of files value: {split_value}: {e}")

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
        raise ValueError(f"Unknown split mode: {split_mode}")


def split_pdf(pdf_path, output_dir, split_mode="single_page", split_value=None):
    """Splits a PDF into multiple files based on a specified mode."""
    pdf_path_obj = Path(pdf_path)
    output_folder_obj = Path(output_dir)

    with pikepdf.Pdf.open(pdf_path_obj) as src_pdf:
        total_pages = len(src_pdf.pages)
        if total_pages == 0:
            raise ValueError("PDF file is empty, no pages to split.")

        page_chunks = _get_page_chunks(total_pages, split_mode, split_value)
        output_folder_obj.mkdir(parents=True, exist_ok=True)
        base_filename = pdf_path_obj.stem

        custom_range_strings = []
        if split_mode == "custom_ranges":
            custom_range_strings = [s.strip() for s in str(split_value).split(';') if s.strip()]

        for i, page_list in enumerate(page_chunks):
            with pikepdf.Pdf.new() as output_pdf:
                for page_num in page_list:
                    output_pdf.pages.append(src_pdf.pages[page_num])

                if split_mode == "custom_ranges":
                    range_str = custom_range_strings[i]
                    if range_str.startswith('+'):
                        range_str = range_str[1:]
                    
                    safe_range_name = range_str.replace(':', 's').replace(',', '_')
                    output_name = f"{base_filename}_{safe_range_name}.pdf"
                else:
                    output_name = f"{base_filename}_part_{i + 1:04d}.pdf"

                output_path = output_folder_obj / output_name
                output_pdf.save(output_path)

    print(f"Successfully split {pdf_path} into {len(page_chunks)} PDF files in {output_dir}")


if __name__ == "__main__":
    pdf_path = Path(r"C:\Users\Chian\Desktop\input.pdf")
    output_dir = Path(r"C:\Users\Chian\Desktop\split_output")

    split_pdf(pdf_path, output_dir, split_mode="single_page")
    # split_pdf(pdf_path, output_dir, split_mode="fixed_pages", split_value=5)
    # split_pdf(pdf_path, output_dir, split_mode="fixed_files", split_value=3)
    # split_pdf(pdf_path, output_dir, split_mode="custom_ranges", split_value="1-3;+5-7,6;8-")
