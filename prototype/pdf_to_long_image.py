import pypdfium2 as pdfium
from PIL import Image


def pdf_to_long_image(pdf_path, output_image_path, dpi=300, quality=85):
    """
    Convert a PDF to a single long image by concatenating all pages vertically.
    
    Args:
        pdf_path: Path to the input PDF file
        output_image_path: Path to save the output image
        dpi: DPI for rendering (default 300)
        quality: JPEG quality for output (default 85)
    """
    with pdfium.PdfDocument(pdf_path) as doc:
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF file has no pages.")

        page_images = []
        total_width = 0
        total_height = 0

        for i in range(total_pages):
            page = doc[i]
            # Render the page to an image
            page_width, page_height = page.get_width(), page.get_height()
            
            # Define render options
            bitmap = page.render(
                scale=dpi/72,  # uses 72 as base DPI
                rotation=0,
                crop=(0, 0, page_width, page_height)
            )
            
            img = bitmap.to_pil()

            page_images.append(img)
            total_width = max(total_width, img.width)
            total_height += img.height
            print(f"Processed page {i+1}/{total_pages}")

        if not page_images:
            raise ValueError("No pages were rendered from the PDF.")

    # Create a blank image with the combined height of all pages
    long_image = Image.new("RGB", (total_width, total_height), (255, 255, 255))
    current_y = 0
    for img in page_images:
        long_image.paste(img, (0, current_y))
        current_y += img.height

    long_image.save(output_image_path, format='JPEG', quality=quality)
    print(f"Successfully converted PDF to long image: {output_image_path}")


if __name__ == "__main__":
    # Example usage
    pdf_path = r"C:\Users\Chian\Desktop\input.pdf"
    output_image_path = r"C:\Users\Chian\Desktop\long_image.jpg"
    
    pdf_to_long_image(pdf_path, output_image_path, dpi=300, quality=85)