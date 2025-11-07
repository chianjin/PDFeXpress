from pikepdf import Pdf
from pathlib import Path
from typing import Set


def _parse_pages_to_delete(range_string: str, total_pages: int) -> Set[int]:
    """
    Parse a range string (e.g. "1,3,5-7") into a set of 0-based page indices to delete.
    Set will auto removes duplicates, no need to check.
    """
    pages_to_delete_set: Set[int] = set()

    for part in range_string.split(","):
        part = part.strip()
        try:
            if "-" in part:
                start_str, end_str = part.split("-", 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
                if not (1 <= start <= end <= total_pages):
                    raise ValueError(
                        f"Invalid page range '{part}': must between 1-{total_pages}."
                    )
                pages_to_delete_set.update(range(start - 1, end))
            else:
                page = int(part)
                if not (1 <= page <= total_pages):
                    raise ValueError(
                        f"Invalid page number '{part}': must between 1-{total_pages}."
                    )
                pages_to_delete_set.add(page - 1)  # Convert to 0-based
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise ValueError(f"Invalid range format '{part}': {e}")

    return pages_to_delete_set


def delete_pages(pdf_path, output_path, pages_to_delete_str):
    """
    Delete specified pages from a PDF file.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to save the output PDF file
        pages_to_delete_str: String specifying pages to delete (e.g. "1,3,5-7")
    """
    with Pdf.open(pdf_path) as pdf:
        total_pages_doc = len(pdf.pages)
        if total_pages_doc == 0:
            raise ValueError("PDF file has no pages.")

        pages_to_delete_set = _parse_pages_to_delete(pages_to_delete_str, total_pages_doc)
        if not pages_to_delete_set:
            raise ValueError(f"No valid pages could be parsed from '{pages_to_delete_str}'.")

        pages_to_keep = [
            p for p in range(total_pages_doc) if p not in pages_to_delete_set
        ]
        if not pages_to_keep:
            raise ValueError(f"Will delete all pages from {Path(pdf_path).name}.")

        # Create a new PDF with only the pages to keep
        with Pdf.new() as output_pdf:
            for page_num in pages_to_keep:
                output_pdf.pages.append(pdf.pages[page_num])
            
            output_pdf.save(output_path)

    print(f"Successfully deleted {len(pages_to_delete_set)} page(s).")


if __name__ == "__main__":
    # Example usage
    pdf_path = Path('temp/example/128.pdf')
    output_path = Path('temp/example/128_delete-pages.pdf')
    pages_to_delete = "1,3,5-7"  # Delete pages 1, 3, and 5-7
    
    delete_pages(pdf_path, output_path, pages_to_delete)