from pikepdf import Pdf


def interleave_pdf(pdf_path_a, pdf_path_b, output_pdf_path, reverse_b=False):
    """
    Interleave pages from two PDF files.
    
    Args:
        pdf_path_a: Path to the first PDF file
        pdf_path_b: Path to the second PDF file
        output_pdf_path: Path to save the output PDF file
        reverse_b: Whether to reverse the order of pages in the second PDF
    """
    with Pdf.open(pdf_path_a) as doc_a, pikepdf.Pdf.open(pdf_path_b) as doc_b:
        len_a = len(doc_a.pages)
        len_b = len(doc_b.pages)
        
        if len_a + len_b == 0:
            raise ValueError("Input files are empty, no pages to merge.")

        with Pdf.new() as output_pdf:
            max_len = max(len_a, len_b)

            for i in range(max_len):
                # Add page from first PDF if it exists
                if i < len_a:
                    output_pdf.pages.append(doc_a.pages[i])

                # Add page from second PDF if it exists
                if i < len_b:
                    page_b_index = (len_b - 1) - i if reverse_b else i
                    output_pdf.pages.append(doc_b.pages[page_b_index])

            output_pdf.save(output_pdf_path)

    print(f"Successfully interleaved PDFs to {output_pdf_path}")


if __name__ == "__main__":
    # Example usage
    pdf_path_a = r"C:\Users\Chian\Desktop\pdf_a.pdf"
    pdf_path_b = r"C:\Users\Chian\Desktop\pdf_b.pdf"
    output_pdf_path = r"C:\Users\Chian\Desktop\interleaved.pdf"
    
    interleave_pdf(pdf_path_a, pdf_path_b, output_pdf_path, reverse_b=False)