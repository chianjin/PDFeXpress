from pathlib import Path
from typing import List

from PIL import Image

A4_PT = (595, 842)
POINTS_PER_INCH = 72


def images_to_pdf(
    image_paths: List[str | Path],
    output_pdf_path: str | Path,
    target_pagesize_pt: tuple[float, float] = None
):
    """Converts a list of images into a single PDF file."""
    processed_images = []
    for image_path in image_paths:
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB for PDF compatibility, preserving transparency.
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # If a target page size is given, scale the image to fit that page.
                if target_pagesize_pt:
                    page_width_pt, page_height_pt = target_pagesize_pt
                    page_px_width = int(page_width_pt / POINTS_PER_INCH * 300)
                    page_px_height = int(page_height_pt / POINTS_PER_INCH * 300)

                    page_img = Image.new('RGB', (page_px_width, page_px_height), (255, 255, 255))
                    img.thumbnail((page_px_width, page_px_height), Image.Resampling.LANCZOS)

                    paste_x = (page_px_width - img.width) // 2
                    paste_y = (page_px_height - img.height) // 2
                    page_img.paste(img, (paste_x, paste_y))
                    processed_images.append(page_img)
                # Otherwise, use the image's own size.
                else:
                    processed_images.append(img.copy())

        except Exception as e:
            print(f"Could not process image {image_path}: {e}")
            continue

    if not processed_images:
        raise ValueError("No valid images found to convert to PDF.")

    first_img_dpi = processed_images[0].info.get('dpi', (100.0, 100.0))[0]

    processed_images[0].save(
        output_pdf_path,
        "PDF",
        resolution=first_img_dpi,
        save_all=True,
        append_images=processed_images[1:]
    )


if __name__ == '__main__':
    image_list_a = [f"temp/output/128/page_{i}.jpg" for i in range(1, 3)]
    pdf_path_a = 'temp/output/images_to_pdf_physical_size.pdf'
    images_to_pdf(image_list_a, pdf_path_a)
    print(f"Successfully created PDF (physical size) at {pdf_path_a}")

    image_list_b = [f"temp/output/128/page_{i}.jpg" for i in range(3, 5)]
    pdf_path_b = 'temp/output/images_to_pdf_a4_fit.pdf'
    images_to_pdf(image_list_b, pdf_path_b, target_pagesize_pt=A4_PT)
    print(f"Successfully created PDF (A4 fit) at {pdf_path_b}")