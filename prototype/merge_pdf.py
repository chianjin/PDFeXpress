from pathlib import Path
from typing import List
from pikepdf import Pdf, OutlineItem

translation_table = str.maketrans("-_.,", "    ")


def replace_special_chars(text):
    return text.translate(translation_table)


def _add_bookmarks_to_pdf(pdf, bookmark_positions):
    """
    Add bookmarks to pdf
    bookmark_positions: A list containing position information for each PDF that needs a bookmark
    """
    if not bookmark_positions:
        return

    with pdf.open_outline() as outline:
        for file_path, start_page_idx in bookmark_positions:
            bookmark_title = replace_special_chars(Path(file_path).stem)
            
            # Ensure page index is within range
            target_page_idx = min(start_page_idx, len(pdf.pages) - 1)
            
            # Create bookmark item and add to root node
            outline_item = OutlineItem(bookmark_title, target_page_idx)
            outline.root.append(outline_item)


def merge_pdf(input_files: List[Path], output_file: Path, create_bookmarks: bool = False):
    """
    Merge multiple PDF files into a single PDF.
    
    Args:
        input_files: List of paths to PDF files to merge
        output_file: Path to save the merged PDF file
        create_bookmarks: Whether to create bookmarks for each merged file
    """
    with Pdf.new() as output_pdf:
        # List for bookmark entries
        bookmark_positions = []
        current_page = 0

        for i, file_path in enumerate(input_files):
            with Pdf.open(file_path) as input_pdf:
                if create_bookmarks:
                    # Record positions where bookmarks are needed
                    bookmark_positions.append((file_path, current_page))
                
                # Append all pages from input PDF to output PDF
                for page in input_pdf.pages:
                    output_pdf.pages.append(page)
                
                current_page += len(input_pdf.pages)
            print(f"Processed {i+1}/{len(input_files)} files")

        # If bookmarks are needed, add them
        if create_bookmarks and bookmark_positions:
            _add_bookmarks_to_pdf(output_pdf, bookmark_positions)

        output_pdf.save(output_file)

    print(f"Successfully merged {len(input_files)} PDFs to {output_file}")


if __name__ == "__main__":
    # Example usage
    input_files = [
        Path(r"C:\Users\Chian\Desktop\pdf1.pdf"),
        Path(r"C:\Users\Chian\Desktop\pdf2.pdf"),
        Path(r"C:\Users\Chian\Desktop\pdf3.pdf"),
    ]
    output_file = Path(r"C:\Users\Chian\Desktop\merged.pdf")
    
    merge_pdf(input_files, output_file, create_bookmarks=True)