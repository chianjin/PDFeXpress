from pathlib import Path
from typing import List

from pikepdf import Pdf, OutlineItem


def _replace_special_chars(text: str) -> str:
    """Replaces special characters in a string with spaces for clean bookmark titles."""
    translation_table = str.maketrans("-_.,", "    ")
    return text.translate(translation_table)


def _add_bookmarks_to_pdf(pdf: Pdf, bookmark_positions: List):
    """Adds bookmarks to a PDF based on a list of titles and page indices."""
    if not bookmark_positions:
        return

    with pdf.open_outline() as outline:
        for file_path, start_page_idx in bookmark_positions:
            bookmark_title = _replace_special_chars(Path(file_path).stem)
            target_page_idx = min(start_page_idx, len(pdf.pages) - 1)
            outline_item = OutlineItem(bookmark_title, target_page_idx)
            outline.root.append(outline_item)


def merge_pdf(
    input_files: List[Path],
    output_file: Path,
    create_bookmarks: bool = False,
    force_duplex: bool = False
):
    """Merges multiple PDF files into one, with options for bookmarks and duplex layout."""
    with Pdf.new() as output_pdf:
        bookmark_positions = []
        current_page = 0

        for i, file_path in enumerate(input_files):
            with Pdf.open(file_path) as input_pdf:
                if create_bookmarks:
                    bookmark_positions.append((file_path, current_page))

                output_pdf.pages.extend(input_pdf.pages)
                current_page += len(input_pdf.pages)

                if force_duplex and (current_page % 2 != 0) and (i < len(input_files) - 1):
                    output_pdf.add_blank_page()
                    current_page += 1

            print(f"Processed {i + 1}/{len(input_files)} files")

        if create_bookmarks and bookmark_positions:
            _add_bookmarks_to_pdf(output_pdf, bookmark_positions)

        output_pdf.save(output_file)

    print(f"Successfully merged {len(input_files)} PDFs to {output_file}")


if __name__ == "__main__":
    input_paths = [
        Path(r"C:\Users\Chian\Desktop\pdf1.pdf"),
        Path(r"C:\Users\Chian\Desktop\pdf2.pdf"),
        Path(r"C:\Users\Chian\Desktop\pdf3.pdf"),
    ]
    output_path = Path(r"C:\Users\Chian\Desktop\merged.pdf")

    merge_pdf(input_paths, output_path, create_bookmarks=True, force_duplex=True)
