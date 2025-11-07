from pathlib import Path
from typing import List

from pikepdf import Pdf, Rectangle

A4_WIDTH, A4_HEIGHT = 595, 842
STANDARD_INVOICE_HEIGHT_MM = 140
STANDARD_INVOICE_HEIGHT_PTS = STANDARD_INVOICE_HEIGHT_MM * 2.83465
TOLERANCE = 10


def _is_a4_size(width: float, height: float) -> bool:
    """Checks if the given dimensions correspond to an A4 page size."""
    is_a4_portrait = (
        abs(width - A4_WIDTH) <= TOLERANCE and abs(height - A4_HEIGHT) <= TOLERANCE
    )
    is_a4_landscape = (
        abs(width - A4_HEIGHT) <= TOLERANCE and abs(height - A4_WIDTH) <= TOLERANCE
    )
    return is_a4_portrait or is_a4_landscape


def _is_standard_invoice(pdf_path: str | Path) -> bool:
    """Checks if a PDF is a standard single-page A5 invoice."""
    with Pdf.open(pdf_path) as doc:
        if len(doc.pages) != 1:
            return False
        page = doc.pages[0]
        width = float(page.MediaBox[2])
        height = float(page.MediaBox[3])
        is_a5_width = abs(width - A4_WIDTH) <= TOLERANCE
        is_standard_height = abs(height - STANDARD_INVOICE_HEIGHT_PTS) <= TOLERANCE
        return is_a5_width and is_standard_height


def merge_invoices(invoice_pdf_paths: List[Path], output_pdf_path: Path):
    """Merges multiple invoice PDFs into a single A4-formatted PDF."""
    if not invoice_pdf_paths:
        raise ValueError("No invoice files provided.")

    standard_invoice_paths = []
    other_invoice_paths = []

    for pdf_path in invoice_pdf_paths:
        if _is_standard_invoice(pdf_path):
            standard_invoice_paths.append(pdf_path)
        else:
            other_invoice_paths.append(pdf_path)

    with Pdf.new() as final_pdf:
        # Place two standard A5 invoices onto a single A4 page.
        i = 0
        while i < len(standard_invoice_paths):
            new_page = final_pdf.add_blank_page(page_size=(A4_WIDTH, A4_HEIGHT))

            with Pdf.open(standard_invoice_paths[i]) as doc1:
                first_page = doc1.pages[0]
                new_page.add_overlay(first_page, Rectangle(0, A4_HEIGHT / 2, A4_WIDTH, A4_HEIGHT))

            if i + 1 < len(standard_invoice_paths):
                with Pdf.open(standard_invoice_paths[i + 1]) as doc2:
                    second_page = doc2.pages[0]
                    new_page.add_overlay(second_page, Rectangle(0, 0, A4_WIDTH, A4_HEIGHT / 2))
            
            i += 2

        # Place other invoices on their own A4 pages, aligning at the top.
        for pdf_path in other_invoice_paths:
            with Pdf.open(pdf_path) as doc:
                for page in doc.pages:
                    page_width = float(page.MediaBox[2])
                    page_height = float(page.MediaBox[3])
                    
                    if _is_a4_size(page_width, page_height):
                        final_pdf.pages.append(page)
                    else:
                        new_page = final_pdf.add_blank_page(page_size=(A4_WIDTH, A4_HEIGHT))
                        new_page.add_overlay(page, Rectangle(0, 0, page_width, page_height))

        final_pdf.save(output_pdf_path)

    print(f"Successfully merged {len(invoice_pdf_paths)} invoices to {output_pdf_path}")


if __name__ == "__main__":
    invoice_paths = [
        Path(r"C:\Users\Chian\Desktop\invoice1.pdf"),
        Path(r"C:\Users\Chian\Desktop\invoice2.pdf"),
        Path(r"C:\Users\Chian\Desktop\invoice3.pdf"),
    ]
    output_path = Path(r"C:\Users\Chian\Desktop\merged_invoices.pdf")
    
    merge_invoices(invoice_paths, output_path)
