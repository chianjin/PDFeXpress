from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory, askopenfilename
from typing import Union

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_PDF
from modules import extract_images
from ui.UiExtractImages import UiExtractImages


class ExtractImages(UiExtractImages):
    def __init__(self, master=None, **kw):
        super(ExtractImages, self).__init__(master, **kw)
        self._page_no_width = 1
        self._pdf_file: Union[str, Path] = ''
        self._images_dir: Union[str, Path] = ''
        self._page_count = 0
        self._use_src_dir = 0
        self.use_src_dir.set(self._use_src_dir)

    def get_pdf_file(self):
        old_pdf_file = self._pdf_file
        self._pdf_file = askopenfilename(filetypes=FILE_TYPES_PDF, title='选择 PDF 文件')
        if self._pdf_file:
            self._pdf_file = Path(self._pdf_file)
            if old_pdf_file != self._pdf_file:
                self.pdf_file.set(self._pdf_file)
                self.set_use_src_dir()
                with fitz.Document(str(self._pdf_file)) as pdf:
                    self._page_count = pdf.page_count
                self._page_no_width = len(str(self._page_count))
                self.app_info.set(f'共 {self._page_count} 页。')
                self.process_info.set('')
                self._toggle_buttons()

    def set_images_dir(self):
        old_images_dir = self._images_dir
        self._images_dir = askdirectory(title='选择图像输出目录')
        if self._images_dir:
            self._images_dir = Path(self._images_dir)
            if old_images_dir != self._images_dir:
                self.images_dir.set(self._images_dir)
                if self._images_dir == self._pdf_file.parent:
                    self._use_src_dir = 1
                else:
                    self._use_src_dir = 0
                self.use_src_dir.set(self._use_src_dir)
                self.process_info.set('')
                self._toggle_buttons()

    def set_use_src_dir(self):
        old_images_dir = self._images_dir
        self._use_src_dir = self.use_src_dir.get()
        if self._pdf_file and self._use_src_dir:
            self._images_dir = self._pdf_file.parent
            if old_images_dir != self._images_dir:
                self.images_dir.set(self._images_dir)
                self.process_info.set('')
                self._toggle_buttons()

    def process(self):
        queue = Queue()
        sub_process = Process(
                target=extract_images,
                args=(queue, self._pdf_file, self._images_dir)
                )
        sub_process_list = [sub_process]
        sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=self._page_count)

    def _toggle_buttons(self):
        if self._pdf_file and self._images_dir:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'
