from pathlib import Path
from typing import List
from pikepdf import Pdf, Array, Page, String, Name, OutlineItem


def _get_page_number(self: OutlineItem):
    page_number = None
    if self.destination:
        if isinstance(self.destination, Array):
            # 12.3.2.2 Explicit destination
            # [raw_page, /PageLocation.SomeThing, integer parameters for viewport]
            raw_page = self.destination[0]
            page = Page(raw_page)
            page_number = page.label
        elif isinstance(self.destination, String):
            # 12.3.2.2 Named destination, byte string reference to Names
            page_number = (
                f"<Named Destination in document .Root.Names dictionary: "
                f"{self.destination}>"
            )
        elif isinstance(self.destination, Name):
            # 12.3.2.2 Named destination, name object (PDF 1.1)
            page_number = (
                f"<Named Destination in document .Root.Dests dictionary: "
                f"{self.destination}>"
            )
        elif isinstance(self.destination, int):
            # Page number
            page_number = f'<Page {self.destination}>'
    else:
        page_number = '<Action>'

    return page_number

OutlineItem.page_number = property(_get_page_number)

def _get_outline_items(outline_item: OutlineItem, outline_list: List = None, level=0):
    level += 1
    if outline_list is None:
        outline_list = []
    outline_list.append([level, outline_item.page_number, outline_item.title])
    for item in outline_item.children:
        _get_outline_items(item, outline_list, level)

def get_outlines(pdf_path: str | Path) -> List:
    outlines = []
    with Pdf.open(pdf_path) as pdf:
        with pdf.open_outline() as outline:
            if outline.root:
                for item in outline.root:
                        _get_outline_items(item, outlines)
    return outlines

def set_outlines(pdf_path: str, outlines: List, output_path: str):
    with Pdf.open(pdf_path) as pdf:
        with pdf.open_outline() as outline:
            outline.root.clear()
            
            if not outlines:
                # If no outlines provided, just save the PDF without bookmarks
                pdf.save(output_path)
                return

            item_node: dict[int, OutlineItem] = {}
            for level, page, title in outlines:
                try:
                    page = int(page)
                except ValueError:
                    continue

                item = OutlineItem(title, int(page)-1)
                item_node[level] = item
                if level == 1:
                    outline.root.append(item)
                else:
                    try:
                        item_node[level-1].children.append(item)
                    except KeyError:
                        raise ValueError(f"Invalid parent item for bookmark: {title}")
        # Save the PDF with the new outline
        pdf.save(output_path)

def import_from_csv(csv_path: str) -> List:
    outline_list = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f:
            # Skip lines starting with ';'
            if line.strip().startswith(';'):
                continue
            
            # fixed columns width
            try:
                level = int(line[:6].strip())
                page = int(line[6:12].strip())
                title = line[12:].strip()
                outline_list.append([level, page, title])
            except ValueError:
                # Skip rows with invalid data
                continue
    return outline_list

def export_to_csv(outline_list: List, csv_path: str):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        # Write format description
        f.write("; This file contains bookmark information for a PDF file.\n")
        f.write("; level and page columns have fixed width of 6 characters.\n")
        f.write("; level page title\n")
        
        # Write data with fixed column widths
        for item in outline_list:
            if len(item) >= 3:
                level, page, title = item[0], item[1], item[2]
                # Format with fixed column widths: level and page with 6 chars width
                formatted_line = f"{str(level):<6}{str(page):<6}{title}\n"
                f.write(formatted_line)


if __name__ == "__main__":
    # Example usage
    pdf_path = Path('temp/example/document_with_outline.pdf')
    output_path = Path('temp/output/document_with_outline_bookmark.pdf')
    csv_path = Path('temp/output/bookmarks.csv')
    new_csv_path = Path('temp/example/new_bookmarks.csv')
    
    # Get outlines from existing PDF
    outlines = get_outlines(pdf_path)
    print(f"Found {len(outlines)} outlines")
    
    # Export to CSV
    export_to_csv(outlines, csv_path)
    
    # Import from CSV
    imported_outlines = import_from_csv(new_csv_path)
    print(imported_outlines)
    print(f"Imported {len(imported_outlines)} outlines")
    
    # Set outlines to a new PDF
    set_outlines(pdf_path, imported_outlines, output_path)