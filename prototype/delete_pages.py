from pathlib import Path
from typing import Set

from pikepdf import Pdf


def _parse_pages_to_delete(range_string: str, total_pages: int) -> Set[int]:
    """Parses a page range string into a set of 0-based page indices."""
    pages_to_delete = set()
    for part in range_string.split(','):
        part = part.strip()
        if not part:
            continue

        try:
            if "-" in part:
                start_str, end_str = part.split("-", 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
                if not (1 <= start <= end <= total_pages):
                    raise ValueError(f"Invalid range '{part}': must be between 1-{total_pages}.")
                pages_to_delete.update(range(start - 1, end))
            else:
                page = int(part)
                if not (1 <= page <= total_pages):
                    raise ValueError(f"Invalid page '{part}': must be between 1-{total_pages}.")
                pages_to_delete.add(page - 1)
        except ValueError as e:
            raise ValueError(f"Invalid range format for '{part}': {e}")

    return pages_to_delete


def delete_pages(pdf_path: Path, output_path: Path, pages_to_delete_str: str):
    """Deletes specified pages from a PDF file."""
    with Pdf.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        if total_pages == 0:
            raise ValueError("PDF file has no pages.")

        pages_to_delete = _parse_pages_to_delete(pages_to_delete_str, total_pages)
        if not pages_to_delete:
            raise ValueError(f"No valid pages could be parsed from '{pages_to_delete_str}'.")

        if len(pages_to_delete) == total_pages:
            raise ValueError(f"This operation would delete all pages from the PDF.")

        for page_index in sorted(list(pages_to_delete), reverse=True):
            del pdf.pages[page_index]

        pdf.save(output_path)

    print(f"Successfully deleted {len(pages_to_delete)} page(s).")


if __name__ == "__main__":
    pdf_path = Path('temp/example/128.pdf')
    output_path = Path('temp/example/128_delete-pages.pdf')
    pages_to_delete = "1,3,5-7"

    delete_pages(pdf_path, output_path, pages_to_delete)
