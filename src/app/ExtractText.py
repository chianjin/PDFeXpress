from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

import fitz
from tkinterdnd2 import DND_FILES

from app.Progress import Progress
from constants import FILE_TYPES_PDF, FILE_TYPES_TEXT
from ui.UiExtractText import UiExtractText
from utils import check_dir, check_file_exist, get_pdf_info, pdf_info, split_drop_data


class ExtractText(UiExtractText):
    def __init__(self, master=None, **kw):
        super(ExtractText, self).__init__(master, **kw)

        self._page_count = 0
        self._pdf_file: str | Path = ''
        self._text_file: str | Path = ''

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_file)

    def drop_file(self, event):
        file_list = split_drop_data(event.data)
        for file in file_list:
            if file.suffix.lower() in FILE_TYPES_PDF[0][1]:
                self._pdf_file, self._page_count, _other = pdf_info(file)
                break
        self._set_options()

    def get_pdf_file(self):
        self._pdf_file, self._page_count, _other = get_pdf_info()
        self._set_options()

    def _set_options(self):
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(_('Total Pages: {}').format(self._page_count))
            self._text_file = self._pdf_file.with_suffix('.txt')
            self.text_file.set(self._text_file)
        self._toggle_buttons()

    def set_text_file(self):
        if self._text_file:
            initial_file = self._text_file.name
        else:
            initial_file = ''
        self._text_file = asksaveasfilename(
                title=_('Select text file'),
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
