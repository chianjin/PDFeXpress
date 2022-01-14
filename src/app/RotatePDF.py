from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_PDF
from ui.UiRotatePDF import UiRotatePDF
from utils import check_dir, check_file_exist, get_pdf_info


class RotatePDF(UiRotatePDF):
    def __init__(self, master=None, **kw):
        super(RotatePDF, self).__init__(master, **kw)

        self._pdf_file: Path | str = ''
        self._rotated_pdf_file: Path | str = ''
        self._page_count = 0

    def get_pdf_file(self):
        self._pdf_file, self._page_count, _width = get_pdf_info()
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(_('Total Pages: {}').format(self._page_count))
            self._rotated_pdf_file = self._pdf_file.with_suffix('.Rotated.pdf')
            self.rotated_pdf_file.set(self._rotated_pdf_file)
        self._toggle_buttons()

    def set_rotated_pdf_file(self):
        if self._rotated_pdf_file:
            initial_file = self._rotated_pdf_file.name
        else:
            initial_file = ''
        rotated_pdf_file = asksaveasfilename(
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                title=_('Select rotated PDF file'),
                initialfile=initial_file
                )
        if rotated_pdf_file:
            self._rotated_pdf_file = Path(rotated_pdf_file)
            self.rotated_pdf_file.set(self._rotated_pdf_file)

        self._toggle_buttons()

    def process(self):
        if not check_file_exist(self._pdf_file):
            return None
        check_dir(self._rotated_pdf_file.parent)

        queue = Queue()
        sub_process = Process(
                target=rotate_pdf,
                args=(queue, self._pdf_file, self._rotated_pdf_file, self.rotate_degree.get())
                )
        sub_process_list = [sub_process]
        sub_process.start()
        progress = Progress(process_list=sub_process_list, queue=queue, maximum=self._page_count)
        self.wait_window(progress)

    def _toggle_buttons(self):
        if self._pdf_file and self._rotated_pdf_file:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'


def rotate_pdf(queue: Queue, pdf_file: Union[str, Path, None], rotated_pdf_file: Union[str, Path], rotation: int):
    with fitz.Document(pdf_file) as pdf:
        for page_no, page in enumerate(pdf):
            page.set_rotation(rotation=rotation)
            queue.put(page_no)
        pdf.save(rotated_pdf_file)
