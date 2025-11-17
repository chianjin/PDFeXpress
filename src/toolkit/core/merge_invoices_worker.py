import pymupdf

from toolkit.i18n import gettext_text as _

# Constants for page sizes in points (1 inch = 72 points, 1 mm = 2.83465 points)
A4_WIDTH, A4_HEIGHT = 595, 842
STANDARD_INVOICE_HEIGHT_MM = 140
STANDARD_INVOICE_HEIGHT_PTS = STANDARD_INVOICE_HEIGHT_MM * 2.83465
TOLERANCE = 10  # Tolerance for dimension checks


def _is_a4_size(rect: pymupdf.Rect) -> bool:
    """Check if a rectangle's size is approximately A4."""
    is_a4_portrait = (
        abs(rect.width - A4_WIDTH) <= TOLERANCE
        and abs(rect.height - A4_HEIGHT) <= TOLERANCE
    )
    is_a4_landscape = (
        abs(rect.width - A4_HEIGHT) <= TOLERANCE
        and abs(rect.height - A4_WIDTH) <= TOLERANCE
    )
    return is_a4_portrait or is_a4_landscape


def _is_standard_invoice(doc: pymupdf.Document) -> bool:
    """Check if a document is a standard single-page invoice."""
    if len(doc) != 1:
        return False
    page = doc[0]
    is_a5_width = abs(page.rect.width - A4_WIDTH) <= TOLERANCE
    is_standard_height = (
        abs(page.rect.height - STANDARD_INVOICE_HEIGHT_PTS) <= TOLERANCE
    )
    return is_a5_width and is_standard_height


def merge_invoices_worker(
    invoice_pdf_paths: list[str],
    output_pdf_path: str,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        if not invoice_pdf_paths:
            raise ValueError(_('No invoice files provided.'))

        progress_queue.put(('INIT', len(invoice_pdf_paths)))

        standard_invoice_paths: list[str] = []
        other_invoice_paths: list[str] = []

        for i, pdf_path in enumerate(invoice_pdf_paths):
            if cancel_event.is_set():
                raise InterruptedError
            with pymupdf.open(pdf_path) as doc:
                if _is_standard_invoice(doc):
                    standard_invoice_paths.append(pdf_path)
                else:
                    other_invoice_paths.append(pdf_path)
            progress_queue.put(('PROGRESS', i + 1))

        with pymupdf.open() as final_doc:
            for i in range(0, len(standard_invoice_paths), 2):
                if cancel_event.is_set():
                    raise InterruptedError

                page = final_doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)

                with pymupdf.open(standard_invoice_paths[i]) as doc1:
                    doc1.bake()
                    page.show_pdf_page(
                        pymupdf.Rect(0, 0, A4_WIDTH, A4_HEIGHT / 2), doc1, 0
                    )

                if i + 1 < len(standard_invoice_paths):
                    with pymupdf.open(standard_invoice_paths[i + 1]) as doc2:
                        doc2.bake()
                        page.show_pdf_page(
                            pymupdf.Rect(0, A4_HEIGHT / 2, A4_WIDTH, A4_HEIGHT), doc2, 0
                        )

            for pdf_path in other_invoice_paths:
                if cancel_event.is_set():
                    raise InterruptedError
                with pymupdf.open(pdf_path) as doc:
                    doc.bake()
                    for p_idx, p in enumerate(doc):
                        if _is_a4_size(p.rect):
                            final_doc.insert_pdf(doc, from_page=p_idx, to_page=p_idx)
                        else:
                            new_page = final_doc.new_page(
                                width=A4_WIDTH, height=A4_HEIGHT
                            )
                            new_page.show_pdf_page(
                                pymupdf.Rect(0, 0, p.rect.width, p.rect.height),
                                doc,
                                p_idx,
                            )

            if cancel_event.is_set():
                raise InterruptedError

            progress_queue.put(('SAVING', _('Saving merged PDF...')))
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    raise InterruptedError
                saving_ack_event.wait(timeout=0.1)

            final_doc.save(output_pdf_path, garbage=4, deflate=True)

        success_msg = _('Merged {} invoices.').format(len(invoice_pdf_paths))
        result_queue.put(('SUCCESS', success_msg))

    except InterruptedError:
        result_queue.put(('CANCEL', _('Cancelled by user.')))
    except Exception as e:
        result_queue.put(('ERROR', _('Unexpected error occurred. {}').format(e)))
