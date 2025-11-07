from pathlib import Path
from typing import List
from pikepdf import Pdf, Rectangle

# Constants for page sizes in points (1 inch = 72 points, 1 mm = 2.83465 points)
A4_WIDTH, A4_HEIGHT = 595, 842
STANDARD_INVOICE_HEIGHT_MM = 140
STANDARD_INVOICE_HEIGHT_PTS = STANDARD_INVOICE_HEIGHT_MM * 2.83465
TOLERANCE = 10  # Tolerance for dimension checks


def _is_a4_size(width: float, height: float) -> bool:
    """Check if a rectangle's size is approximately A4."""
    is_a4_portrait = (
        abs(width - A4_WIDTH) <= TOLERANCE
        and abs(height - A4_HEIGHT) <= TOLERANCE
    )
    is_a4_landscape = (
        abs(width - A4_HEIGHT) <= TOLERANCE
        and abs(height - A4_WIDTH) <= TOLERANCE
    )
    return is_a4_portrait or is_a4_landscape


def _is_standard_invoice(pdf_path: str | Path) -> bool:
    """Check if a document is a standard single-page invoice."""
    with Pdf.open(pdf_path) as doc:
        if len(doc.pages) != 1:
            return False
        page = doc.pages[0]
        width = float(page.MediaBox[2])  # MediaBox[2] is the width
        height = float(page.MediaBox[3])  # MediaBox[3] is the height
        is_a5_width = abs(width - A4_WIDTH) <= TOLERANCE
        is_standard_height = abs(height - STANDARD_INVOICE_HEIGHT_PTS) <= TOLERANCE
        return is_a5_width and is_standard_height


def merge_invoices(invoice_pdf_paths: List[Path], output_pdf_path: Path):
    """
    Merge invoice PDFs, combining two standard invoices onto one A4 page.
    
    Args:
        invoice_pdf_paths: List of paths to invoice PDF files to merge
        output_pdf_path: Path to save the merged PDF file
    """
    if not invoice_pdf_paths:
        raise ValueError("No invoice files provided.")

    standard_invoice_paths = []
    other_invoice_paths = []

    # Classify invoices
    for pdf_path in invoice_pdf_paths:
        if _is_standard_invoice(pdf_path):
            standard_invoice_paths.append(pdf_path)
        else:
            other_invoice_paths.append(pdf_path)

    with Pdf.new() as final_pdf:
        # Process Standard Invoices
        i = 0
        while i < len(standard_invoice_paths):
            # Create a new A4 page for the combined invoices
            # Create a temporary PDF with one page to hold both invoices
            with Pdf.new() as temp_page_pdf:
                temp_page = temp_page_pdf.add_blank_page(page_size=(A4_WIDTH, A4_HEIGHT))

                # Add first invoice to top half
                with Pdf.open(standard_invoice_paths[i]) as doc1:
                    if len(doc1.pages) > 0:
                        first_page = doc1.pages[0]
                        # Add as overlay to top half of A4 page
                        temp_page.add_overlay(first_page, 
                                             Rectangle(0, A4_HEIGHT/2, A4_WIDTH, A4_HEIGHT))

                # Add second invoice to bottom half if available
                if i + 1 < len(standard_invoice_paths):
                    with Pdf.open(standard_invoice_paths[i + 1]) as doc2:
                        if len(doc2.pages) > 0:
                            second_page = doc2.pages[0]
                            # Add as overlay to bottom half of A4 page
                            temp_page.add_overlay(second_page, 
                                                 Rectangle(0, 0, A4_WIDTH, A4_HEIGHT/2))

                # Add the combined page to final PDF
                final_pdf.pages.append(temp_page)

            i += 2  # Process two invoices at a time

        # Process Other Invoices
        for pdf_path in other_invoice_paths:
            with Pdf.open(pdf_path) as doc:
                for page in doc.pages:
                    # Check if page is A4 size
                    page_width = float(page.MediaBox[2])
                    page_height = float(page.MediaBox[3])
                    
                    if _is_a4_size(page_width, page_height):
                        # If A4 size, add directly
                        final_pdf.pages.append(page)
                    else:
                        # If not A4 size, create new A4 page and add the content
                        with Pdf.new() as temp_pdf:
                            new_page = temp_pdf.add_blank_page(page_size=(A4_WIDTH, A4_HEIGHT))
                            
                            # Add the original page content to the new A4 page at the top
                            new_page.add_overlay(page, Rectangle(0, 0, page_width, page_height))
                            
                            # Add the new page to final PDF
                            final_pdf.pages.append(new_page)

        final_pdf.save(output_pdf_path)

    print(f"Successfully merged {len(invoice_pdf_paths)} invoices to {output_pdf_path}")


if __name__ == "__main__":
    # Example usage
    invoice_pdf_paths = [
        Path(r"C:\Users\Chian\Desktop\invoice1.pdf"),
        Path(r"C:\Users\Chian\Desktop\invoice2.pdf"),
        Path(r"C:\Users\Chian\Desktop\invoice3.pdf"),
    ]
    output_pdf_path = Path(r"C:\Users\Chian\Desktop\merged_invoices.pdf")
    
    merge_invoices(invoice_pdf_paths, output_pdf_path)