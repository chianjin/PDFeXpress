# toolkit/core/edit_bookmark_worker.py


from pathlib import Path
from typing import List

from pikepdf import Pdf, Array, Page, String, Name, OutlineItem

from toolkit.i18n import gettext_text as _


def _get_page_number(self: OutlineItem):
    """Get page number of OutlineItem"""
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
    """Get outlines from OutlineItem"""
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
    """
    Sets outlines (bookmarks) in a PDF based on the provided outline list and saves the result.
    
    Args:
        pdf_path (str): Path to the input PDF file
        outlines (List): List of [level, page, title] lists representing bookmarks (page is 1-based)
        output_path (str): Path to save the output PDF with bookmarks
    """
    with Pdf.open(pdf_path) as pdf:
        # Create a new outline
        with pdf.open_outline() as outline:
            # Clear any existing outline
            outline.root.clear()
            
            if not outlines:
                # If no outlines provided, just save the PDF without bookmarks
                pdf.save(output_path)
                return
            
            # Current stack of parent items in the outline hierarchy
            # Each entry is a tuple (level, outline_item)
            parent_stack = []
            
            for item in outlines:
                if len(item) < 3:
                    continue  # Skip invalid items
                
                level, page, title = item[0], item[1], item[2]
                
                # Convert page to int if needed (page is 1-based, PDF pages are 0-based)
                try:
                    page_num = int(page) - 1  # Convert from 1-indexed to 0-indexed
                except ValueError:
                    continue  # Skip if page number is invalid
                
                # Find the correct parent based on level
                # Remove items from stack that are at the same or deeper level
                while parent_stack and parent_stack[-1][0] >= level:
                    parent_stack.pop()
                
                # Create the destination for the bookmark (page number)
                # Page numbers in PDF are 0-indexed
                if 0 <= page_num < len(pdf.pages):
                    # Create the new outline item - use zero-based page number directly
                    outline_item = OutlineItem(title, page_num)
                    
                    # Add to appropriate parent
                    if parent_stack:
                        # Add as child to the last item in the stack at the level above
                        parent_outline = parent_stack[-1][1]
                        parent_outline.children.append(outline_item)
                    else:
                        # Add as a root-level item
                        outline.root.append(outline_item)
                    
                    # Add this item to the stack as a potential parent for deeper levels
                    parent_stack.append((level, outline_item))
        
        # Save the PDF with the new outline
        pdf.save(output_path)

def import_from_csv(csv_path: str) -> List:
    """
    Imports outlines (bookmarks) from a CSV file.
    
    Args:
        csv_path (str): Path to the CSV file containing bookmarks
        
    Returns:
        List: List of [level, page, title] lists representing bookmarks
    """
    outline_list = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        for line in f:
            # Skip lines starting with ';'
            if line.strip().startswith(';'):
                continue
            
            # Split by tab to get fields
            row = line.split('\t')
            if len(row) >= 3:
                try:
                    # level and page should be in fixed 8-char width, strip whitespace
                    level = int(row[0].strip())
                    page = int(row[1].strip())
                    # Title might contain multiple tabs, so join the rest
                    title = '\t'.join(row[2:]).rstrip('\n')  # Remove trailing newline
                    outline_list.append([level, page, title])
                except ValueError:
                    # Skip rows with invalid data
                    continue
    return outline_list

def export_to_csv(outline_list: List, csv_path: str):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        # Write format description
        f.write(_("; This file contains bookmark information for a PDF file\n"))
        f.write(_("; Format: level <tab>page  <tab>title\n"))
        f.write(_("; level and page columns have fixed width of 6 characters\n"))
        # Write header with leading ';'
        f.write(_("; level \tpage    \ttitle\n"))
        
        # Write data with fixed column widths
        for item in outline_list:
            if len(item) >= 3:
                level, page, title = item[0], item[1], item[2]
                # Format with fixed column widths: level and page with 8 chars width
                formatted_line = f"{str(level):<6}\t{str(page):<6}\t{title}\n"
                f.write(formatted_line)

