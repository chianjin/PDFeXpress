import pikepdf
from pathlib import Path
from typing import List, Any


def _parse_page_ranges(range_string: str, total_pages: int) -> List[List[int]]:
    """
    Parse a range string (e.g. "1,3,5-7") into a list of page index lists.
    """
    chunks: List[List[int]] = []
    if not range_string:
        raise ValueError("Custom range string cannot be empty.")
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
                        f"Invalid range '{part}': must be between 1-{total_pages}, and start <= end."
                    )
                chunk = list(range(start - 1, end))  # Convert to 0-based
            else:
                page: int = int(part)
                if page < 1 or page > total_pages:
                    raise ValueError(
                        f"Invalid page '{part}': must be between 1-{total_pages}."
                    )
                chunk = [page - 1]  # Convert to 0-based
            chunks.append(chunk)
        except Exception as e:
            raise ValueError(
                f"Invalid custom range '{part}' format: {str(e)}"
            )
    return chunks


def _get_page_chunks(
    total_pages: int, split_mode: str, split_value: Any
) -> List[List[int]]:
    """
    Get page chunks based on split mode.
    """
    if split_mode == "single_page":
        return [[i] for i in range(total_pages)]

    elif split_mode == "fixed_pages":
        try:
            num = int(split_value)
            if num <= 0:
                raise ValueError("Value must be greater than 0")
        except Exception:
            raise ValueError(
                f"Invalid pages per file value: {split_value}"
            )

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
        except Exception:
            raise ValueError(
                f"Invalid number of files value: {split_value}"
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
        raise ValueError(f"Unknown split mode: {split_mode}")


def split_pdf(pdf_path, output_dir, split_mode="single_page", split_value=None):
    """
    Split a PDF file into multiple files based on specified mode.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory to save the split PDF files
        split_mode: How to split the PDF ("single_page", "fixed_pages", "fixed_files", "custom_ranges")
        split_value: Additional value for split mode (e.g., number of pages per file)
    """
    pdf_path_obj = Path(pdf_path)
    output_folder_obj = Path(output_dir)

    with pikepdf.Pdf.open(pdf_path_obj) as src_pdf:
        total_pages = len(src_pdf.pages)
        if total_pages == 0:
            raise ValueError("PDF file is empty, no pages to split.")

        page_chunks = _get_page_chunks(total_pages, split_mode, split_value)
        output_folder_obj.mkdir(parents=True, exist_ok=True)
        base_filename = pdf_path_obj.stem

        for i, page_list in enumerate(page_chunks):
            # Create output PDF inside the loop and use context manager to save it
            with pikepdf.Pdf.new() as output_pdf:
                
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

    print(f"Successfully split {pdf_path} into {len(page_chunks)} PDF files in {output_dir}")


if __name__ == "__main__":
    # Example usage
    pdf_path = Path(r"C:\Users\Chian\Desktop\input.pdf")
    output_dir = Path(r"C:\Users\Chian\Desktop\split_output")
    
    # Split into single-page PDFs
    split_pdf(pdf_path, output_dir, split_mode="single_page")
    
    # Or split into fixed page chunks (e.g. 5 pages per file)
    # split_pdf(pdf_path, output_dir, split_mode="fixed_pages", split_value=5)
    
    # Or split into a fixed number of files (e.g. 3 files)
    # split_pdf(pdf_path, output_dir, split_mode="fixed_files", split_value=3)
    
    # Or split using custom ranges (e.g. "1-3,5,7-10")
    # split_pdf(pdf_path, output_dir, split_mode="custom_ranges", split_value="1-3,5,7-10")