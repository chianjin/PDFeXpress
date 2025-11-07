from pikepdf import Pdf, PdfImage
from pathlib import Path


def extract_images(pdf_path, output_dir, min_width=100, min_height=100, extract_all=False):
    with Pdf.open(pdf_path) as pdf:
        xref_list = []  # Track xrefs to skip duplicates
        image_count = 0
        extract_count = 0
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for page_num, page in enumerate(pdf.pages, start=1):
            # Use page.images to get all images in the page
            for xref in page.images.keys():
                if xref in xref_list:
                    continue  # Skip duplicate image
                xref_list.append(xref)
                try:
                    # Try to parse the object as an image
                    pdf_img = PdfImage(page.images[xref])
                except Exception as e:
                    continue  # Skip non-image XObject
                image_count += 1

                # Check if size requirements are met
                if extract_all or (pdf_img.width >= min_width and pdf_img.height >= min_height):
                    # Use PikePDF's extract_to method with fileprefix, which automatically handles extension
                    image_prefix = output_dir / f"P{page_num:02d}_{xref[1:]}"
                    image_path = pdf_img.extract_to(fileprefix=image_prefix)
                    extract_count += 1
                    print(f"Extracted image {image_path}")

    print(f"Found {image_count} unique images, extracted {extract_count} images.")


if __name__ == "__main__":
    # Example usage
    pdf_path = Path('temp/example/with_image.pdf')
    output_dir = Path('temp/output') / pdf_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extract_images(pdf_path, output_dir)