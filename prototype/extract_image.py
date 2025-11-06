from pikepdf import Pdf, PdfImage
from pathlib import Path

pdf_path = Path(r"C:\Users\Chian\Desktop\喀什市数字化项目\喀什市融媒体中心宣传设备建设项目.pdf")
output_dir = Path(r"C:\Users\Chian\Desktop\pw")

def extract_images(pdf_path, output_dir):
    with (Pdf.open(pdf_path) as pdf):
        image_key_list = []
        for page_index, page in enumerate(pdf.pages, start=1):
            for key in page.images.keys():
                if key in image_key_list:
                    continue
                image_key_list.append(key)
                print(f'Processing page {page_index} image {key}')
                image_dir = output_dir / pdf_path.stem
                image_dir.mkdir(parents=True, exist_ok=True)
                image_prefix = image_dir / f'P{page_index}_{key[1:]}'
                raw_image =  page.images[key]
                pdf_img = PdfImage(raw_image)
                image_path = pdf_img.extract_to(fileprefix=image_prefix)
                print(f'Saved image to {image_path}')

extract_images(pdf_path, output_dir)