from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from PIL import Image

POINTS_PER_INCH = 72
DEFAULT_ASSUMED_DPI = 96


def images_to_pdf(
        image_list: list[Path | str],
        output_pdf_path: Path | str,
        target_pagesize: tuple[float, float] = None
):

    canvas = Canvas(output_pdf_path, pagesize=target_pagesize or A4)

    # 假设所有路径都是有效的
    target_width_pt, target_height_pt = (target_pagesize if target_pagesize else (0, 0))

    for image_path in image_list:

        image = Image.open(image_path)
        pixel_width, pixel_height = image.size
        draw_x, draw_y = 0.0, 0.0

        # --- mode A: fix physical size ---
        if not target_pagesize:

            x_dpi, y_dpi = image.info.get('dpi', (DEFAULT_ASSUMED_DPI, DEFAULT_ASSUMED_DPI))

            # 计算 PDF 页面尺寸 (pt)
            pdf_width_pt = (pixel_width / x_dpi) * POINTS_PER_INCH
            pdf_height_pt = (pixel_height / y_dpi) * POINTS_PER_INCH

            canvas.setPageSize((pdf_width_pt, pdf_height_pt))
            draw_width, draw_height = pdf_width_pt, pdf_height_pt

        # --- mode B: fit size specified ---
        else:
            pdf_width_pt, pdf_height_pt = target_width_pt, target_height_pt
            canvas.setPageSize(target_pagesize)

            image_aspect_ratio = pixel_width / pixel_height
            page_aspect_ratio = pdf_width_pt / pdf_height_pt

            if image_aspect_ratio > page_aspect_ratio:
                draw_width = pdf_width_pt
                draw_height = draw_width / image_aspect_ratio
                draw_y = (pdf_height_pt - draw_height) / 2.0
            else:
                draw_height = pdf_height_pt
                draw_width = draw_height * image_aspect_ratio
                draw_x = (pdf_width_pt - draw_width) / 2.0

        # 核心绘制命令
        canvas.drawImage(
            str(image_path),
            x=draw_x,
            y=draw_y,
            width=draw_width,
            height=draw_height,
            preserveAspectRatio=False
        )

        canvas.showPage()

    canvas.save()

if __name__ == '__main__':

    image_list = [f"temp/output/128/page_{i}.jpg"  for i in range(1, 10)]
    pdf_path = 'temp/output/128_images_to_pdf.pdf'

    images_to_pdf(image_list, pdf_path)
