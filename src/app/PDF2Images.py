from io import BytesIO
from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory
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

        self.ComboboxImageDPI.configure(values=IMAGE_DPI)

        self._pdf_file: Union[str, Path] = ''
        self._page_count = 0
        self._page_no_width = 1
        self._images_dir: Union[str, Path] = ''
        self._image_format = 'png'
        self._image_alpha = 1
        self._image_quality = 85
        self._image_dpi = 192

        self.image_format.set(self._image_format)
        self.image_alpha.set(self._image_alpha)
        self.image_quality.set(self._image_quality)
        self.image_dpi.set(self._image_dpi)

    def get_pdf_file(self):
        self._pdf_file, self._page_count, self._page_no_width = get_pdf_info()
        if self._page_count > 0:
            self._pdf_file = Path(self._pdf_file)
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(_('Total Pages: {}').format(self._page_count))
            self._images_dir = self._pdf_file.parent
            self.images_dir.set(self._images_dir)
        self._toggle_buttons()

    def set_images_dir(self):
        self._images_dir = askdirectory(title=_('Select images folder'))
        if self._images_dir:
            self._images_dir = Path(self._images_dir)
            self.images_dir.set(self._images_dir)
        self._toggle_buttons()

    def set_image_format(self):
        self._image_format = self.image_format.get()
        if self._image_format == 'png':
            self.CheckbuttonPNGAlpha.configure(state='normal')
            self.LabelImageQuality.configure(state='disabled')
            self.EntryImageQuality.configure(state='disabled')
            self.ScaleImageQuality.configure(state='disabled')
            self.LabelImageDPI.configure(state='disabled')
            self.ComboboxImageDPI.configure(state='disabled')
        else:
            self.CheckbuttonPNGAlpha.configure(state='disabled')
            self.LabelImageQuality.configure(state='normal')
            self.EntryImageQuality.configure(state='normal')
            self.ScaleImageQuality.configure(state='normal')
            self.LabelImageDPI.configure(state='normal')
            self.ComboboxImageDPI.configure(state='normal')

    def set_image_alpha(self):
        self._image_alpha = self.image_alpha.get()

    def valid_image_quality(self, d, P, V):
        if d == '0' \
                or d == '1' and P == '0' \
                or d == '1' and not P.startswith('0') and P.isdigit() and 0 <= int(P) <= 100 \
                or V == 'focusout' and P.isdigit() and 0 <= int(P) <= 100:
            if self.EntryImageQuality.grab_status():
                self.EntryImageQuality.grab_release()
            return True

        self.EntryImageQuality.grab_set()
        self.EntryImageQuality.focus()
        return False

    def set_image_quality(self, scale_value):
        image_quality = self.ScaleImageQuality.get()
        self._image_quality = int(image_quality / 5) * 5
        self.image_quality.set(self._image_quality)

    def valid_image_dpi(self, d, P, V):
        if d == '0' \
                or d == '1' and not P.startswith('0') and P.isdigit() and 0 < int(P) \
                or V == 'focusout' and P.isdigit() and 0 < int(P):
            if self.ComboboxImageDPI.grab_status():
                self.ComboboxImageDPI.grab_release()
            return True

        self.ComboboxImageDPI.grab_set()
        self.ComboboxImageDPI.focus()
        return False

    def process(self):
        if not check_file_exist(self._pdf_file):
            return None
        check_dir(self._images_dir)

        pdf_range = range(self._page_count)
        page_range_list = []
        for start in range(PHYSICAL_CPU_COUNT):
            # if PHYSICAL_CPU_COUNT == 4
            # [0, 4, 8, ...], [1, 5, 9, ...], [2, 6, 10, ...], [3, 7, 11, ...]
            page_range = pdf_range[start::PHYSICAL_CPU_COUNT]
            page_range_list.append(page_range)
        page_range_list = [page_range for page_range in page_range_list if len(page_range)]

        queue = Queue()
        sub_process_list = []
        for page_range in page_range_list:
            sub_process = Process(
                    target=pdf2images,
                    args=(
                            queue, self._pdf_file, self._images_dir, self._image_format,
                            bool(self._image_alpha), self._image_quality, self._image_dpi, page_range
                            )
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
        image_format: str, image_alpha: bool, image_quality: int, image_dpi: int, page_range: Iterable
        ):
    zoom = image_dpi / 96 * 4 / 3  # actually 72
    matrix = fitz.Matrix(zoom, zoom)
    with fitz.Document(pdf_file) as pdf:
        page_no_width = len(str(pdf.page_count))
        for page_no in page_range:
            image_file = f'{image_dir / pdf_file.stem}-P{page_no + 1:0{page_no_width}d}.{image_format}'
            image_alpha = False if image_format == 'jpg' else image_alpha
            pixmap = pdf[page_no].get_pixmap(matrix=matrix, alpha=image_alpha)
            if image_format == 'png':
                pixmap.save(image_file)
            else:  # JPEG
                image = Image.open(BytesIO(pixmap.tobytes()))
                image.save(image_file, quality=image_quality, dpi=(image_dpi, image_dpi))
                image.close()
            queue.put(page_no)
