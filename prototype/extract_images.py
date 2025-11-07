from pathlib import Path

from pikepdf import Pdf, PdfImage


def extract_images(
    pdf_path: Path,
    output_dir: Path,
    min_width: int = 100,
    min_height: int = 100,
    extract_all: bool = False
):
    """Extracts images from a PDF file and saves them to a directory."""
    with Pdf.open(pdf_path) as pdf:
        xref_set = set()
        image_count = 0
        extract_count = 0

        output_dir.mkdir(parents=True, exist_ok=True)

        for page_num, page in enumerate(pdf.pages, start=1):
            for xref_str in page.images.keys():
                if xref_str in xref_set:
                    continue
                xref_set.add(xref_str)

                try:
                    pdf_img = PdfImage(page.images[xref_str])
                except Exception:
                    continue
                image_count += 1

                if extract_all or (pdf_img.width >= min_width and pdf_img.height >= min_height):
                    image_prefix = output_dir / f"P{page_num:02d}_{xref_str[1:]}"
                    image_path = pdf_img.extract_to(fileprefix=str(image_prefix))
                    extract_count += 1
                    print(f"Extracted image {image_path}")

    print(f"Found {image_count} unique images, extracted {extract_count} images.")


if __name__ == "__main__":
    pdf_path = Path('temp/example/with_image.pdf')
    output_dir = Path('temp/output') / pdf_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    extract_images(pdf_path, output_dir)
