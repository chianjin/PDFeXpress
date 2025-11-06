import pypdfium2 as pdfium

def pdf_to_image(
        pdf_path,
        output_dir,
        dpi=300,
        output_format='png',
        transparent_background=True,
        quality=85
):
    with pdfium.PdfDocument(pdf_path) as doc:
        image_dir = output_dir / pdf_path.stem
        image_dir.mkdir(parents=True, exist_ok=True)

        for page_num, page in enumerate(doc):
            image_path = image_dir / f'page_{page_num + 1}.{output_format}'

            if output_format == 'png' and transparent_background:
                pil_image  = page.render(
                    scale=dpi / 72,
                    fill_color=(255, 255, 255, 0),
                    maybe_alpha=True
                ).to_pil()
                pil_image.save(image_path, format='PNG', dpi=(dpi, dpi), optimize=True)
            else:
                pil_image = page.render(
                    scale=dpi / 72
                ).to_pil()
                pil_image.save(image_path, format='JPEG', quality=quality, dpi=(dpi, dpi), optimize=True)


if __name__ == '__main__':
    from pathlib import Path
    pdf_path = Path(r"C:\Users\Chian\Desktop\进博会\招商处\128.pdf")
    output_dir = Path(r'C:\Users\Chian\Desktop\pw')
    pdf_to_image(pdf_path, output_dir)