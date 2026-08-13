"""edit_bookmarks worker (synchronous, no subprocess).

Single-input PDF -> single-output PDF with a user-edited table of contents.
Editing a TOC is fast (one open + set_toc + save), so no multiprocessing or
progress dialog is used; the frame calls ``apply_bookmarks()`` directly.
"""

import csv

import pymupdf


def apply_bookmarks(input_path, output_path, toc):
    """Write ``toc`` into ``input_path`` and save to ``output_path``.

    ``toc`` is a list of ``[level, title, page]`` with **1-based** page
    numbers (matching ``Document.get_toc()`` / ``Document.set_toc()``).
    """
    doc = pymupdf.open(str(input_path))
    try:
        doc.set_toc(toc)
        doc.save(str(output_path))
    finally:
        doc.close()


def read_csv_bookmarks(path):
    """Read bookmarks from a CSV file.

    Expected columns: level, page, title. A leading header row is skipped
    when its first field is not an integer. Returns a list of
    ``[level, page, title]`` (ints / str, page 1-based).
    """
    rows = []
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        first = True
        for rec in reader:
            if not rec:
                continue
            if first:
                first = False
                try:
                    int(rec[0])
                except (ValueError, IndexError):
                    continue  # header row
            if len(rec) < 2:
                continue
            level = int(rec[0])
            page = int(rec[1])
            title = rec[2] if len(rec) > 2 else ''
            rows.append([level, page, title])
    return rows


def write_csv_bookmarks(path, rows):
    """Write ``rows`` (list of [level, page, title]) to a CSV (UTF-8 BOM)."""
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['level', 'page', 'title'])
        for level, page, title in rows:
            writer.writerow([level, page, title])
