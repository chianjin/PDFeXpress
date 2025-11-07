from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


def pdf_to_long_image(
    pdf_path: Path,
    output_image_path: Path,
    dpi: int = 300,
    quality: int = 85
):
    """Renders a PDF into a single long vertical image."""
    with pdfium.PdfDocument(pdf_path) as doc:
        if not doc:
            raise ValueError("PDF file has no pages.")

        page_images = []
        total_width = 0
        total_height = 0

        for i in range(len(doc)):
            page = doc[i]
            bitmap = page.render(scale=dpi / 72)
            img = bitmap.to_pil()

            page_images.append(img)
            total_width = max(total_width, img.width)
            total_height += img.height
            print(f"Processed page {i + 1}/{len(doc)}")

        if not page_images:
            raise ValueError("No pages were rendered from the PDF.")

    long_image = Image.new("RGB", (total_width, total_height), (255, 255, 255))
    current_y = 0
    for img in page_images:
        long_image.paste(img, (0, current_y))
        current_y += img.height

    long_image.save(output_image_path, format='JPEG', quality=quality)
    print(f"Successfully converted PDF to long image: {output_image_path}")


if __name__ == "__main__":
    pdf_path = Path(r"C:\Users\Chian\Desktop\input.pdf")
    output_image_path = Path(r"C:\Users\Chian\Desktop\long_image.jpg")

    pdf_to_long_image(pdf_path, output_image_path, dpi=300, quality=85)
