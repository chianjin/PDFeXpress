from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_TEXT
from ui.UiExtractText import UiExtractText
from utils import get_pdf_info, check_dir, check_file_exist


class ExtractText(UiExtractText):
    def __init__(self, master=None, **kw):
        super(ExtractText, self).__init__(master, **kw)
        self._page_count = 0
        self._pdf_file: str | Path = ''
        self._text_file: str | Path = ''

    def get_pdf_file(self):
        self._pdf_file, self._page_count, _ = get_pdf_info()
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(f'共 {self._page_count} 页。')
            self._text_file = self._pdf_file.with_suffix('.txt')
            self.text_file.set(self._text_file)
        self._toggle_buttons()

    def set_text_file(self):
        if self._text_file:
            initial_file = self._text_file.name
        else:
            initial_file = ''
        self._text_file = asksaveasfilename(
                title='选择输出文件名',
                filetypes=FILE_TYPES_TEXT,
                defaultextension='.txt',
                initialfile=initial_file
                )
        if self._text_file:
            self._text_file = Path(self._text_file)
            self.text_file.set(self._text_file)
        self._toggle_buttons()

    def process(self):
        if not check_file_exist(self._pdf_file):
            return None
        check_dir(self._text_file.parent)

        queue = Queue()
        sub_process = Process(
                target=extract_text,
                args=(queue, self._pdf_file, self._text_file)
                )
        sub_process_list = [sub_process]
        sub_process.start()
        progress = Progress(process_list=sub_process_list, queue=queue, maximum=self._page_count)
        self.wait_window(progress)

    def _toggle_buttons(self):
        if self._pdf_file and self._text_file:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'


def extract_text(queue: Queue, pdf_file: Union[str, Path, None], text_file: Union[str, Path]):
    contents = []
    with fitz.Document(pdf_file) as pdf:
        for page_no, page in enumerate(pdf, start=1):
            contents.append(page.get_text())
            queue.put(page_no)
    with open(text_file, 'w', encoding='UTF-8') as text:
        text.write(''.join(contents))
