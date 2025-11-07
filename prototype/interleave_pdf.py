from pathlib import Path

from pikepdf import Pdf


def interleave_pdf(
    pdf_path_a: Path,
    pdf_path_b: Path,
    output_pdf_path: Path,
    reverse_b: bool = False
):
    """Interleaves the pages of two PDF files into a single PDF."""
    with Pdf.open(pdf_path_a) as doc_a, Pdf.open(pdf_path_b) as doc_b:
        len_a = len(doc_a.pages)
        len_b = len(doc_b.pages)

        if len_a + len_b == 0:
            raise ValueError("Input files are empty, no pages to merge.")

        with Pdf.new() as output_pdf:
            max_len = max(len_a, len_b)

            for i in range(max_len):
                if i < len_a:
                    output_pdf.pages.append(doc_a.pages[i])

                if i < len_b:
                    page_b_index = (len_b - 1) - i if reverse_b else i
                    output_pdf.pages.append(doc_b.pages[page_b_index])

            output_pdf.save(output_pdf_path)

    print(f"Successfully interleaved PDFs to {output_pdf_path}")


if __name__ == "__main__":
    pdf_a_path = Path(r"C:\Users\Chian\Desktop\pdf_a.pdf")
    pdf_b_path = Path(r"C:\Users\Chian\Desktop\pdf_b.pdf")
    output_path = Path(r"C:\Users\Chian\Desktop\interleaved.pdf")

    interleave_pdf(pdf_a_path, pdf_b_path, output_path, reverse_b=False)
