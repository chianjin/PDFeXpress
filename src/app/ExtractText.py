from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_PDF, FILE_TYPES_TEXT
from modules import extract_text
from ui.UiExtractText import UiExtractText


class ExtractText(UiExtractText):
    def __init__(self, master=None, **kw):
        super(ExtractText, self).__init__(master, **kw)
        self._page_count = 0
        self._pdf_file: str | Path = ''
        self._text_file: str | Path = ''
        self._use_src_dir = 0
        self.use_src_dir.set(self._use_src_dir)

    def get_pdf_file(self):
        old_pdf_file = self._pdf_file
        self._pdf_file = askopenfilename(title='选择 PDF 文件', filetypes=FILE_TYPES_PDF)
        if self._pdf_file:
            self._pdf_file = Path(self._pdf_file)
            if old_pdf_file != self._pdf_file:
                self.pdf_file.set(self._pdf_file)
                self.set_use_src_dir()
                with fitz.Document(str(self._pdf_file)) as pdf:
                    self._page_count = pdf.page_count
                self.app_info.set(f'共 {self._page_count} 页。')
                self.process_info.set()
                self._toggle_buttons()

    def set_text_file(self):
        if self._pdf_file:
            text_filename = f'{self._pdf_file.stem}.txt'
        else:
            text_filename = ''
        old_text_file = self._text_file
        self._text_file = asksaveasfilename(
                title='选择输出文本文件名', filetypes=FILE_TYPES_TEXT,
                defaultextension='.txt', initialfile=text_filename
                )
        if self._text_file:
            self._text_file = Path(self._text_file)
            if old_text_file != self._text_file:
                self.text_file.set(self._text_file)
                if self._text_file.parent == self._pdf_file.parent:
                    self._use_src_dir = 1
                else:
                    self._use_src_dir = 0
                self.use_src_dir.set(self._use_src_dir)
                self.process_info.set('')
                self._toggle_buttons()

    def set_use_src_dir(self):
        old_text_file = self._text_file
        self._use_src_dir = self.use_src_dir.get()
        if self._pdf_file and self._use_src_dir:
            self._text_file = f'{self._pdf_file.parent / self._pdf_file.stem}.txt'
            if old_text_file != self._text_file:
                self.text_file.set(self._text_file)
                self.process_info.set('')
                self._toggle_buttons()

    def process(self):
        queue = Queue()
        sub_process = Process(
                target=extract_text,
                args=(queue, self._pdf_file, self._text_file)
                )
        sub_process_list = [sub_process]
        sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=self._page_count)

    def _toggle_buttons(self):
        if self._pdf_file and self._text_file:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'
