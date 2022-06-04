from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory
from typing import Union

import fitz
from tkinterdnd2 import DND_FILES

from app.Progress import Progress
from constants import FILE_TYPES_PDF, PHYSICAL_CPU_COUNT
from ui.UiExtractImages import UiExtractImages
from utils import check_dir, check_file_exist, get_pdf_info, pdf_info, split_drop_data


class ExtractImages(UiExtractImages):
    def __init__(self, master=None, **kw):
        super(ExtractImages, self).__init__(master, **kw)

        self._page_no_width = 1
        self._pdf_file: Union[str, Path] = ''
        self._images_dir: Union[str, Path] = ''
        self._page_count = 0

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_file)

    def drop_file(self, event):
        file_list = split_drop_data(event.data)
        for file in file_list:
            if file.suffix.lower() in FILE_TYPES_PDF[0][1]:
                self._pdf_file, self._page_count, self._page_no_width = pdf_info(file)
                break
        self._set_options()

    def get_pdf_file(self):
        self._pdf_file, self._page_count, self._page_no_width = get_pdf_info()
        self._set_options()

    def _set_options(self):
        if self._page_count > 0:
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

    def process(self):
        if not check_file_exist(self._pdf_file):
            return None
        check_dir(self._images_dir)

        queue = Queue()
        sub_process_list = []

        pdf_range = range(self._page_count)
        for start in range(PHYSICAL_CPU_COUNT):
            page_range = pdf_range[start::PHYSICAL_CPU_COUNT]
            if len(page_range):
                sub_process = Process(
                        target=extract_images,
                        args=(queue, self._pdf_file, self._images_dir, page_range)
                        )
                sub_process_list.append(sub_process)
        for sub_process in sub_process_list:
            sub_process.start()
        progress = Progress(process_list=sub_process_list, queue=queue, maximum=self._page_count)
        self.wait_window(progress)

    def _toggle_buttons(self):
        if self._pdf_file and self._images_dir:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'


def extract_images(queue: Queue, pdf_file: Union[str, Path, None], image_dir: Union[str, Path], page_range):
    with fitz.Document(pdf_file) as pdf:
        page_no_width = len(str(pdf.page_count + 1))
        image_filename = f'{image_dir}/{pdf_file.stem}'
        for page_no in page_range:
            image_list = pdf[page_no].get_images()
            for image_no, image_info in enumerate(image_list):
                xref, *_info = image_info
                image_data = pdf.extract_image(xref)
                ext = image_data['ext']
                image = image_data['image']
                image_file = f'{image_filename}-P{page_no + 1:0{page_no_width}d}-{image_no:d}.{ext}'
                with open(image_file, 'wb') as f:
                    f.write(image)
            queue.put(page_no)
