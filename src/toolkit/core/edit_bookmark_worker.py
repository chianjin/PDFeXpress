"""Worker module to edit PDF bookmarks."""

import csv
from typing import Any

import pymupdf


def get_bookmarks(pdf_path: str) -> list[Any]:
    """Get bookmarks from a PDF file."""
    with pymupdf.open(pdf_path) as doc:
        toc = doc.get_toc()
    return toc


def set_bookmarks(pdf_path: str, toc: list[Any], output_path: str) -> None:
    """Set bookmarks to a PDF file and save to output path."""
    with pymupdf.open(pdf_path) as doc:
        doc.set_toc(toc)
        doc.save(output_path)


def import_bookmarks_from_csv(csv_path: str) -> list[Any]:
    """Import bookmarks from a CSV file."""
    toc = []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
        if not rows:
            return []
        # Check if the first row is a header
        first_row = rows[0]
        start_index = 0
        if 'level' in first_row and 'page' in first_row and 'title' in first_row:
            start_index = 1
        for i in range(start_index, len(rows)):
            row = rows[i]
            if len(row) == 3 and row[0].isdigit() and row[1].isdigit():
                toc.append([int(row[0]), row[2], int(row[1])])
    return toc


def export_bookmarks_to_csv(toc: list[Any], csv_path: str) -> None:
    """Export bookmarks to a CSV file."""
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['level', 'page', 'title'])  # Add header
        for item in toc:
            writer.writerow([item[0], item[2], item[1]])
