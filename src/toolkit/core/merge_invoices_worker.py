# toolkit/core/merge_invoices_worker.py

from typing import List
from pikepdf import Pdf, Rectangle

from toolkit.i18n import gettext_text as _

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


def _is_standard_invoice(pdf_path: str) -> bool:
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


def merge_invoices_worker(
    invoice_pdf_paths: List[str],
    output_pdf_path: str,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        if not invoice_pdf_paths:
            raise ValueError(_("No invoice files provided."))

        progress_queue.put(("INIT", len(invoice_pdf_paths)))

        standard_invoice_paths: List[str] = []
        other_invoice_paths: List[str] = []

        # --- 1. Classify invoices ---
        for i, pdf_path in enumerate(invoice_pdf_paths):
            if cancel_event.is_set():
                raise InterruptedError
            if _is_standard_invoice(pdf_path):
                standard_invoice_paths.append(pdf_path)
            else:
                other_invoice_paths.append(pdf_path)
            progress_queue.put(("PROGRESS", i + 1))

        with Pdf.new() as final_pdf:
            # --- 2. Process Standard Invoices ---
            i = 0
            while i < len(standard_invoice_paths):
                if cancel_event.is_set():
                    raise InterruptedError

                # Create a new A4 page for the combined invoices
                a4_rect = Rectangle(0, 0, A4_WIDTH, A4_HEIGHT)
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

            # --- 3. Process Other Invoices ---
            for pdf_path in other_invoice_paths:
                if cancel_event.is_set():
                    raise InterruptedError
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

            if cancel_event.is_set():
                raise InterruptedError

            # --- 4. Save Final PDF ---
            progress_queue.put(("SAVING", _("Saving merged PDF...")))
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    raise InterruptedError
                saving_ack_event.wait(timeout=0.1)

            final_pdf.save(output_pdf_path)

        success_msg = _("Merged {} invoices.").format(len(invoice_pdf_paths))
        result_queue.put(("SUCCESS", success_msg))

    except InterruptedError:
        result_queue.put(("CANCEL", _("Cancelled by user.")))
    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))
