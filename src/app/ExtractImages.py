from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory
from typing import Union

from app.Progress import Progress
from modules import extract_images
from ui.UiExtractImages import UiExtractImages
from utils import get_pdf_info


class ExtractImages(UiExtractImages):
    def __init__(self, master=None, **kw):
        super(ExtractImages, self).__init__(master, **kw)
        self._page_no_width = 1
        self._pdf_file: Union[str, Path] = ''
        self._images_dir: Union[str, Path] = ''
        self._page_count = 0

    def get_pdf_file(self):
        self._pdf_file, self._page_count, self._page_no_width = get_pdf_info()
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(f'共 {self._page_count} 页')
        self._toggle_buttons()

    def set_images_dir(self):
        self._images_dir = askdirectory(title='选择图像输出目录')
        if self._images_dir:
            self._images_dir = Path(self._images_dir)
            self.images_dir.set(self._images_dir)
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
