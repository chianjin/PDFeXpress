# src/toolkit/core/edit_bookmark_worker.py
import csv
from typing import List

import pymupdf

def get_bookmarks(pdf_path: str) -> List:
    with pymupdf.open(pdf_path) as doc:
        toc = doc.get_toc()
    return toc

def set_bookmarks(pdf_path: str, toc: List, output_path: str):
    with pymupdf.open(pdf_path) as doc:
        doc.set_toc(toc)
        doc.save(output_path)

def import_bookmarks_from_csv(csv_path: str) -> List:
    toc = []
    with open(csv_path, 'r', encoding='utf-8') as f:
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

def export_bookmarks_to_csv(toc: List, csv_path: str):
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['level', 'page', 'title'])  # Add header
        for item in toc:
            writer.writerow([item[0], item[2], item[1]])
