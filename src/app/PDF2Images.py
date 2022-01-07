from io import BytesIO
from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from typing import Iterable, Union

import fitz
from PIL import Image

from app.Progress import Progress
from constants import PHYSICAL_CPU_COUNT
from ui.UiPDF2Images import UiPDF2Images
from utils import check_dir, check_file_exist, get_pdf_info

IMAGE_DPI = '96 144 192 288 384 480 576'
PROGRESS_BAR_DELAY = 80


class PDF2Images(UiPDF2Images):
    def __init__(self, master=None, **kw):
        super(PDF2Images, self).__init__(master, **kw)
        self._pdf_file: Union[str, Path] = ''
        self._page_count = 0
        self._page_no_width = 1
        self._images_dir: Union[str, Path] = ''
        self.ComboboxImageDPI.configure(values=IMAGE_DPI)
        self._image_dpi = 192
        self.image_dpi.set(self._image_dpi)
        self._image_quality = 85
        self.image_quality.set(self._image_quality)

    def get_pdf_file(self):
        self._pdf_file, self._page_count, self._page_no_width = get_pdf_info()
        if self._page_count > 0:
            self._pdf_file = Path(self._pdf_file)
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(f'共 {self._page_count} 页。')
            self._images_dir = self._pdf_file.parent
            self.images_dir.set(self._images_dir)
        self._toggle_buttons()

    def set_images_dir(self):
        self._images_dir = askdirectory(title='选择图像输出目录')
        if self._images_dir:
            self._images_dir = Path(self._images_dir)
            self.images_dir.set(self._images_dir)
        self._toggle_buttons()

    def valid_image_dpi(self):
        image_dpi = self.ComboboxImageDPI.get()
        if image_dpi.isdigit() and int(image_dpi) > 1:
            self._image_dpi = self.image_dpi.get()
            return True
        else:
            showerror(title='错误', message='请输入大于 0 的整数。')
            self.ComboboxImageDPI.focus()
            return False

    def valid_image_quality(self):
        image_quality = self.EntryImageQuality.get()
        if image_quality.isdigit() and 0 <= int(image_quality) <= 100:
            self._image_quality = self.image_quality.get()
            return True
        else:
            showerror(title='错误', message='请输入 0 到 100 的整数。')
            return False

    def set_image_quality(self, scale_value):
        image_quality = self.ScaleImageQuality.get()
        self._image_quality = int(image_quality / 5) * 5
        self.image_quality.set(self._image_quality)

    def process(self):
        if not check_file_exist(self._pdf_file):
            return None
        check_dir(self._images_dir)

        queue = Queue()
        sub_process_list = []

        pdf_range = range(self._page_count)
        for start in range(PHYSICAL_CPU_COUNT):
            # if PHYSICAL_CPU_COUNT == 4
            # [0, 4, 8, ...], [1, 5, 9, ...], [2, 6, 10, ...], [3, 7, 11, ...]
            page_range = pdf_range[start::PHYSICAL_CPU_COUNT]
            if len(page_range) > 0:
                sub_process = Process(
                        target=pdf2images,
                        args=(queue, self._pdf_file, self._images_dir, self._image_quality, self._image_dpi, page_range)
                        )
                sub_process_list.append(sub_process)
        for sub_process in sub_process_list:
            sub_process.start()
        progress = Progress(None, sub_process_list, queue, self._page_count)
        self.wait_window(progress)

    def _toggle_buttons(self):
        if self._pdf_file and self._images_dir:
            self.ButtonProcess.configure(state='normal')
        else:
            self.ButtonProcess.configure(state='disabled')


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
