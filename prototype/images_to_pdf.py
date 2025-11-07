from pathlib import Path
from typing import List
from PIL import Image

# A4 size in points (at 72 DPI)
A4_PT = (595, 842)
POINTS_PER_INCH = 72

def images_to_pdf(
    image_list: List[str | Path], 
    output_pdf_path: str | Path,
    target_pagesize_pt: tuple[float, float] = None
):
    """
    Convert a list of images to a single PDF file, matching the original script's logic.
    
    Args:
        image_list: A list of paths to the image files.
        output_pdf_path: The path to save the output PDF file.
        target_pagesize_pt: Optional. A tuple (width, height) in points for the PDF page.
                           If provided, images are scaled to fit. If None, page size
                           is determined by image's print size.
    """
    processed_images = []
    for image_path in image_list:
        try:
            with Image.open(image_path) as img:
                # Ensure image is in a PDF-compatible mode (RGB)
                if img.mode == 'RGBA':
                    # Create a white background and paste the image onto it
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3]) # Use alpha channel as mask
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # --- Logic to handle page sizing ---
                if target_pagesize_pt:
                    # Mode B: Fit image to a specified page size (e.g., A4)
                    page_width_pt, page_height_pt = target_pagesize_pt
                    
                    # Create a new blank page with the target size
                    # We need to determine the resolution to use. Let's assume 300 DPI for quality.
                    page_px_width = int(page_width_pt / POINTS_PER_INCH * 300)
                    page_px_height = int(page_height_pt / POINTS_PER_INCH * 300)
                    
                    page_img = Image.new('RGB', (page_px_width, page_px_height), (255, 255, 255))
                    
                    # Resize original image to fit on the page while maintaining aspect ratio
                    img.thumbnail((page_px_width, page_px_height), Image.Resampling.LANCZOS)
                    
                    # Paste the resized image onto the center of the page
                    paste_x = (page_px_width - img.width) // 2
                    paste_y = (page_px_height - img.height) // 2
                    page_img.paste(img, (paste_x, paste_y))
                    
                    processed_images.append(page_img)
                else:
                    # Mode A: Use image's own print size. Pillow does this by default.
                    # We just need to pass the image along.
                    processed_images.append(img.copy()) # Use copy to avoid issues with file handles

        except Exception as e:
            print(f"Could not open or convert image {image_path}: {e}")
            continue

    if not processed_images:
        raise ValueError("No valid images found to convert to PDF.")

    # The `resolution` parameter in save() helps mimic the original DPI logic.
    # The original code used image's DPI. Pillow's `save` uses a single `resolution` value.
    # We can extract the DPI from the first image to be more consistent.
    first_img_dpi = processed_images[0].info.get('dpi', (100.0, 100.0))[0]

    processed_images[0].save(
        output_pdf_path, 
        "PDF", 
        resolution=first_img_dpi, 
        save_all=True, 
        append_images=processed_images[1:]
    )

if __name__ == '__main__':
    # Example for Mode A (physical size)
    image_list_a = [f"temp/output/128/page_{i}.jpg" for i in range(1, 3)]
    pdf_path_a = 'temp/output/images_to_pdf_physical_size.pdf'
    images_to_pdf(image_list_a, pdf_path_a)
    print(f"Successfully created PDF (physical size) at {pdf_path_a}")

    # Example for Mode B (fit to A4)
    image_list_b = [f"temp/output/128/page_{i}.jpg" for i in range(3, 5)]
    pdf_path_b = 'temp/output/images_to_pdf_a4_fit.pdf'
    images_to_pdf(image_list_b, pdf_path_b, target_pagesize_pt=A4_PT)
    print(f"Successfully created PDF (A4 fit) at {pdf_path_b}")
