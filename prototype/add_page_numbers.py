import io
from pathlib import Path
from typing import Set

import pikepdf
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))


def _parse_page_selection(range_string: str, total_pages: int) -> Set[int]:
    """Parses a page range string into a set of 0-based page indices."""
    if not range_string:
        return set(range(total_pages))

    page_indices = set()
    parts = range_string.split(',')

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if '-' in part:
            start_str, end_str = part.split('-', 1)
            start = int(start_str.strip()) if start_str.strip() else 1
            end = int(end_str.strip()) if end_str.strip() else total_pages
        else:
            start = int(part)
            end = start

        if not (1 <= start <= end <= total_pages):
            raise ValueError(f"Invalid range '{part}': must be within 1-{total_pages}.")

        page_indices.update(p - 1 for p in range(start, end + 1))

    return page_indices


def add_page_numbers(
    input_pdf_path: Path | str,
    output_pdf_path: Path | str,
    format_string: str = "{page} / {total}",
    page_range: str = None,
    position: str = "bottom-center",
    font_name: str = "Helvetica",
    font_size: int = 10,
    font_color: colors.Color = colors.black,
    margin: int = 50
):
    """Adds page numbers to a PDF file using an overlay method."""
    with pikepdf.Pdf.open(input_pdf_path) as pdf:
        total_pages = len(pdf.pages)
        pages_to_number = _parse_page_selection(page_range, total_pages)

        for i, page in enumerate(pdf.pages):
            if i not in pages_to_number:
                continue

            page_num = i + 1
            text = format_string.format(page=page_num, total=total_pages)

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page.width, page.height))
            
            can.setFont(font_name, font_size)
            can.setFillColor(font_color)

            x, y = 0, 0
            vertical_pos, horizontal_pos = position.split('-')

            if vertical_pos == 'bottom':
                y = margin
            elif vertical_pos == 'top':
                y = page.height - margin

            if horizontal_pos == 'left':
                x = margin
                can.drawString(x, y, text)
            elif horizontal_pos == 'right':
                x = page.width - margin
                can.drawRightString(x, y, text)
            elif horizontal_pos == 'center':
                x = page.width / 2
                can.drawCentredString(x, y, text)
            
            can.save()

            packet.seek(0)
            
            with pikepdf.Pdf.open(packet) as overlay_pdf:
                page.add_overlay(overlay_pdf.pages[0])

        pdf.save(output_pdf_path)

    print(f"Successfully added page numbers to {output_pdf_path}")


if __name__ == '__main__':
    input_file = Path(r"C:\Users\Chian\Desktop\merged.pdf")
    if not input_file.exists():
        print(f"Test file not found at {input_file}, creating a dummy PDF.")
        with pikepdf.Pdf.new() as dummy_pdf:
            for _ in range(10):
                dummy_pdf.add_blank_page()
            dummy_pdf.save(input_file)

    output_dir = Path(r"C:\Users\Chian\Desktop\numbered_output")
    output_dir.mkdir(exist_ok=True)

    add_page_numbers(
        input_file,
        output_dir / "numbered_default.pdf"
    )

    add_page_numbers(
        input_file,
        output_dir / "numbered_custom.pdf",
        format_string="Page {page}",
        page_range="2-8",
        position="top-right",
        font_size=12,
        font_color=colors.red,
        margin=40
    )

    add_page_numbers(
        input_file,
        output_dir / "numbered_bottom_left.pdf",
        format_string="{page}",
        position="bottom-left"
    )

    print(f"Check the folder {output_dir} for the output files.")