# src/toolkit/core/edit_bookmark_worker.py
import pymupdf
from typing import List

def get_bookmarks(pdf_path: str) -> List:
    """
    Reads the table of contents (bookmarks) from a PDF file.
    """
    with pymupdf.open(pdf_path) as doc:
        toc = doc.get_toc()
    return toc

def set_bookmarks(pdf_path: str, toc: List, output_path: str):
    """
    Saves a new table of contents (bookmarks) to a PDF file.
    """
    with pymupdf.open(pdf_path) as doc:
        doc.set_toc(toc)
        doc.save(output_path)

def import_bookmarks_from_csv(csv_path: str) -> List:
    """
    Imports bookmarks from a CSV file.
    Expected format: level,page,title
    """
    import csv
    toc = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) == 3 and row[0].isdigit() and row[1].isdigit():
                toc.append([int(row[0]), row[2], int(row[1])])
    return toc

def export_bookmarks_to_csv(toc: List, csv_path: str):
    """
    Exports bookmarks to a CSV file.
    Format: level,page,title
    """
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        for item in toc:
            writer.writerow([item[0], item[2], item[1]])

