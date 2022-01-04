import os
from io import BytesIO
from multiprocessing import Queue
from pathlib import Path
from tempfile import mkstemp
from typing import Iterable, Union

import fitz
from PIL import Image


def merge_pdf(queue: Queue, pdf_list: list[Path], merged_pdf_file: Path):
    with fitz.Document() as merged_pdf:
        for pdf_no, pdf_file in enumerate(pdf_list, start=1):
            with fitz.Document(str(pdf_file)) as pdf:
                merged_pdf.insert_pdf(pdf)
            queue.put(pdf_no)
        merged_pdf.save(merged_pdf_file)


def split_pdf(
        queue: Queue, pdf_file: Union[str, Path, None], split_pdf_dir: Union[str, Path], split_mode: str,
        split_range_list: tuple[tuple[int]]
        ):
    count = 0
    with fitz.Document(pdf_file) as pdf:
        page_no_width = len(str(pdf.page_count))
        for start, stop in split_range_list:
            if split_mode == 'single':
                _split_pdf_file = f'{split_pdf_dir / pdf_file.stem}-split-P{start + 1:0{page_no_width}d}.pdf'
            else:
                if not stop:
                    stop = pdf.page_count - 1
                _split_pdf_file = f'{split_pdf_dir / pdf_file.stem}-split-' \
                                  f'P{start + 1:0{page_no_width}d}-{stop + 1:0{page_no_width}d}.pdf'

            with fitz.Document() as _split_pdf:
                _split_pdf.insert_pdf(pdf, from_page=start, to_page=stop)
                _split_pdf.save(_split_pdf_file)
            count += 1
            queue.put(count)


def rotate_pdf(queue: Queue, pdf_file: Union[str, Path, None], rotated_pdf_file: Union[str, Path], rotation: int):
    with fitz.Document(pdf_file) as pdf:
        for page_no, page in enumerate(pdf):
            page.set_rotation(rotation=rotation)
            queue.put(page_no)
        pdf.save(rotated_pdf_file)


def extract_images(queue: Queue, pdf_file: Union[str, Path, None], image_dir: Union[str, Path]):
    with fitz.Document(pdf_file) as pdf:
        page_no_width = len(str(pdf.page_count))
        image_filename = f'{image_dir}/{pdf_file.stem}'
        for page_no, page in enumerate(pdf, start=1):
            image_list = page.get_images()
            for image_no, image_info in enumerate(image_list):
                xref, *_info = image_info
                image_data = pdf.extract_image(xref)
                ext = image_data['ext']
                image = image_data['image']
                image_file = f'{image_filename}-P{page_no:0{page_no_width}d}-{image_no:02d}.{ext}'
                with open(image_file, 'wb') as f:
                    f.write(image)
            queue.put(page_no)


def extract_text(queue: Queue, pdf_file: Union[str, Path, None], text_file: Union[str, Path]):
    contents = []
    with fitz.Document(pdf_file) as pdf:
        for page_no, page in enumerate(pdf, start=1):
            contents.append(page.get_text())
            queue.put(page_no)
    with open(text_file, 'w', encoding='UTF-8') as text:
        text.write(''.join(contents))


def pdf2images(
        queue: Queue, pdf_file: Union[str, Path, None], image_dir: Union[str, Path],
        image_quality: int, image_dpi: int, page_range: Iterable
        ):
    zoom = image_dpi / 96 * 4 / 3  # actually 72
    matrix = fitz.Matrix(zoom, zoom)
    with fitz.Document(pdf_file) as pdf:
        page_no_width = len(str(pdf.page_count))
        image_file = f'{image_dir / pdf_file.stem}-P{{:0{page_no_width}d}}.jpg'
        if not page_range:
            page_range = range(pdf.page_count)

        for page_no in page_range:
            pixmap = pdf[page_no].get_pixmap(matrix=matrix)
            image = Image.open(BytesIO(pixmap.tobytes()))
            image.save(image_file.format(page_no + 1), quality=image_quality, dpi=(image_dpi, image_dpi))
            image.close()
            queue.put(page_no)


def images2pdf(queue: Queue, image_list: list[str, Path], pdf_file: Union[str, Path]):
    with fitz.Document() as pdf:
        for image_no, image_file in enumerate(image_list, start=1):
            with fitz.Document(image_file) as image_doc:
                pdf_bytes = image_doc.convert_to_pdf()
                with fitz.Document('images_pdf', pdf_bytes) as image_pdf:
                    pdf.insert_pdf(image_pdf)
            queue.put(image_no)
        pdf.save(pdf_file)


def compress_pdf(
        queue: Queue, pdf_file: Union[str, Path], compressed_pdf_file: Union[str, Path],
        image_quality: int, max_dpi: int, page_range: Iterable, process_id: int
        ):
    with fitz.Document(pdf_file) as pdf:
        for page_no in page_range:
            page = pdf[page_no]
            for image_info in page.get_images():
                # xref, smask, width, height, bpc, colorspace, alt.colorspace, name, filter
                xref, _, width, height, _, _, _, name, _ = image_info
                rect = page.get_image_bbox(name)
                size, dpi = _calculate_size(size=(width, height), rect=rect, max_dpi=max_dpi)
                image_data = pdf.extract_image(xref)
                temp_image = _reduce_image(BytesIO(image_data.get('image')), size=size, quality=image_quality, dpi=dpi)
                contents = page.read_contents()
                contents = contents.replace(bytes(f'/{name} Do', encoding='utf8'), b'')  # remove image invocation
                pdf.update_stream(xref, contents)  # write back contents object
                # insert new image
                page.insert_image(rect, filename=temp_image)
                os.unlink(temp_image)
            # clean unused contents
            page.clean_contents()
            queue.put(page_no)
        sub_compressed_pdf_file = compressed_pdf_file.parent / f'{process_id}-{compressed_pdf_file.name}'
        pdf.save(sub_compressed_pdf_file, deflate=True)


def _reduce_image(image_file, size, quality, dpi):
    image = Image.open(image_file)
    resize_image = image.resize(size)
    fd, temp_file = mkstemp(suffix='.jpg')
    resize_image.save(temp_file, format='jpeg', quality=quality, dpi=(dpi, dpi))
    os.close(fd)
    resize_image.close()
    image.close()
    return temp_file


def _calculate_size(size, rect, max_dpi):
    width, height = size
    rect_width, rect_height = rect.br - rect.tl
    x_dpi = width / rect_width * 72
    y_dpi = height / rect_height * 72
    dpi = min(x_dpi, y_dpi)
    if dpi > max_dpi:
        dpi = max_dpi
    width = int(dpi * rect_width / 72)
    height = int(dpi * rect_height / 72)
    return (width, height), int(dpi)


def merge_compressed_pdf(queue: Queue, compressed_pdf_file: Union[str, Path], page_range_list: Iterable):
    with fitz.Document() as pdf:
        for file_no, page_range in enumerate(page_range_list):
            sub_compressed_pdf_file = compressed_pdf_file.parent / f'{file_no}-{compressed_pdf_file.name}'
            with fitz.Document(sub_compressed_pdf_file) as sub_compressed_pdf:
                pdf.insert_pdf(sub_compressed_pdf, from_page=page_range[0], to_page=page_range[-1])
            # os.unlink(sub_compressed_pdf_file)
            queue.put(file_no)
        pdf.save(compressed_pdf_file, deflate=True)
