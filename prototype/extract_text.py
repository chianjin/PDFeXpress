import pypdfium2 as pdfium
from pathlib import Path

def extract_text(pdf_path, output_path, add_page_separator=True):
    with pdfium.PdfDocument(pdf_path) as doc:
        text_parts = []
        
        for page_num, page in enumerate(doc, start=1):
            text_page = page.get_textpage()
            page_text = text_page.get_text_range()
            page_text = page_text.replace('\r\n', '\n').replace('\r', '\n')
            text_parts.append(page_text)
            # Add a page separator if option is enabled
            if add_page_separator:
                text_parts.append(f"{'='*25} PAGE {page_num+1} END {'='*25}")
        text = '\n'.join(text_parts)
        output_path.write_text(text, encoding="utf-8")
    print(f"Text extracted from {pdf_path} to {output_path}")


if __name__ == "__main__":
    # Example usage
    pdf_path = Path('temp/example/with_image.pdf')
    output_path = Path('temp/output/with_image.txt')
    
    extract_text(pdf_path, output_path, add_page_separator=True)