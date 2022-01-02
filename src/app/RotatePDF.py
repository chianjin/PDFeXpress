from pathlib import Path
from tkinter.filedialog import asksaveasfilename

from constants import FILE_TYPES_PDF
from ui.UiRotatePDF import UiRotatePDF
from utils import get_pdf_info


class RotatePDF(UiRotatePDF):
    def __init__(self, master=None, **kw):
        super(RotatePDF, self).__init__(master, **kw)

        self._pdf_file: Path | str = ''
        self._rotated_pdf_file: Path | str = ''
        self._rotate_degree: int = self.rotate_degree.get()
        self._page_count = 0

    def get_pdf_file(self):
        self._pdf_file, self._page_count, _width = get_pdf_info()
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(f'共 {self._page_count} 页')
        self._toggle_buttons()

    def set_rotated_pdf_file(self):
        if self._rotated_pdf_file:
            initial_file = self._rotated_pdf_file.name
        else:
            if self._pdf_file:
                initial_file = self._pdf_file.with_suffix('.Rotated.pdf')
            else:
                initial_file = ''
        rotated_pdf_file = asksaveasfilename(
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                title='选择旋转的 PDF 文件名',
                initialfile=initial_file
                )
        if rotated_pdf_file:
            self._rotated_pdf_file = Path(rotated_pdf_file)
            self.rotated_pdf_file.set(self._rotated_pdf_file)

        self._toggle_buttons()

    def process(self):
        pass

    def _toggle_buttons(self):
        if self._pdf_file and self._rotated_pdf_file:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'
