from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename

from app.Progress import Progress
from constants import FILE_TYPES_TEXT
from modules import extract_text
from ui.UiExtractText import UiExtractText
from utils import get_pdf_info


class ExtractText(UiExtractText):
    def __init__(self, master=None, **kw):
        super(ExtractText, self).__init__(master, **kw)
        self._page_count = 0
        self._pdf_file: str | Path = ''
        self._text_file: str | Path = ''

    def get_pdf_file(self):
        self._pdf_file, self._page_count = get_pdf_info()
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(f'共 {self._page_count} 页。')
        self._toggle_buttons()

    def set_text_file(self):
        if self._pdf_file:
            initial_file = self._pdf_file.with_suffix('.txt')
            initial_file = initial_file.name
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
