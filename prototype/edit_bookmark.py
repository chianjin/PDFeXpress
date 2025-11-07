from pathlib import Path
from typing import List

from pikepdf import Pdf, OutlineItem


def _get_outline_items(pdf: Pdf, outline_item: OutlineItem, outline_list: List, level: int):
    """Recursively traverses outline items to build a flattened list of bookmarks."""
    level += 1
    page_index = -1
    if outline_item.destination is not None:
        try:
            # Resolve the page object reference to a 0-based page index.
            page_obj = outline_item.destination[0]
            page_index = pdf.pages.index(page_obj)
        except (ValueError, IndexError):
            pass

    outline_list.append([level, page_index + 1, outline_item.title])
    for item in outline_item.children:
        _get_outline_items(pdf, item, outline_list, level)


def get_outlines(pdf_path: str | Path) -> List:
    """Extracts all bookmarks from a PDF into a list format."""
    outlines = []
    with Pdf.open(pdf_path) as pdf:
        with pdf.open_outline() as outline:
            if outline.root:
                for item in outline.root:
                    _get_outline_items(pdf, item, outlines, 0)
    return outlines


def set_outlines(pdf_path: str, outlines: List, output_path: str):
    """Creates a new PDF with the specified bookmark structure."""
    with Pdf.open(pdf_path) as pdf:
        with pdf.open_outline() as outline:
            outline.root.clear()

            if not outlines:
                pdf.save(output_path)
                return

            item_node: dict[int, OutlineItem] = {}
            for level, page, title in outlines:
                try:
                    page = int(page)
                except ValueError:
                    continue

                item = OutlineItem(title, int(page) - 1)
                item_node[level] = item
                if level == 1:
                    outline.root.append(item)
                else:
                    try:
                        item_node[level - 1].children.append(item)
                    except KeyError:
                        raise ValueError(f"Invalid parent item for bookmark: {title}")
        pdf.save(output_path)


def import_from_csv(csv_path: str) -> List:
    """Imports a list of bookmarks from a fixed-width CSV file."""
    outline_list = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(';'):
                continue
            try:
                level = int(line[:6].strip())
                page = int(line[6:12].strip())
                title = line[12:].strip()
                outline_list.append([level, page, title])
            except ValueError:
                continue
    return outline_list


def export_to_csv(outline_list: List, csv_path: str):
    """Exports a list of bookmarks to a fixed-width CSV file."""
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        f.write("; This file contains bookmark information for a PDF file.\n")
        f.write("; level and page columns have fixed width of 6 characters.\n")
        f.write("; level page title\n")

        for item in outline_list:
            if len(item) >= 3:
                level, page, title = item[0], item[1], item[2]
                formatted_line = f"{str(level):<6}{str(page):<6}{title}\n"
                f.write(formatted_line)


if __name__ == "__main__":
    pdf_path = Path('temp/example/document_with_outline.pdf')
    output_path = Path('temp/output/document_with_outline_bookmark.pdf')
    csv_path = Path('temp/output/bookmarks.csv')
    new_csv_path = Path('temp/example/new_bookmarks.csv')

    outlines = get_outlines(pdf_path)
    print(f"Found {len(outlines)} outlines")

    export_to_csv(outlines, csv_path)

    imported_outlines = import_from_csv(new_csv_path)
    print(f"Imported {len(imported_outlines)} outlines")

    set_outlines(pdf_path, imported_outlines, output_path)
