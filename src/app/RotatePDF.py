from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename

from constants import FILE_TYPES_PDF
from ui.UiRotatePDF import UiRotatePDF


class RotatePDF(UiRotatePDF):
    def __init__(self, master=None, **kw):
        super(RotatePDF, self).__init__(master, **kw)
        # self.ComboboxDegree.current(0)
        self.rotate_degree.set('90°')
        self.rotate_direction.set('cw')
        self.use_src_dir.set(0)

    def get_pdf_file(self):
        pdf_file = askopenfilename(filetypes=FILE_TYPES_PDF, title='选择 PDF 文件')
        if pdf_file:
            pdf_path = Path(pdf_file)
            self.pdf_file.set(pdf_path)
            self.set_use_src_dir()

    def set_rotated_pdf_file(self):
        pdf_file = self.pdf_file.get()
        pdf_path = Path(pdf_file)
        rotated_pdf_filename = f'{pdf_path.stem}-rotated.pdf' if pdf_file else ''
        rotated_pdf_file = asksaveasfilename(
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                title='选择输出 PDF 文件名',
                initialfile=rotated_pdf_filename
                )
        if rotated_pdf_file:
            self.rotated_pdf_file.set(Path(rotated_pdf_file))
            self.use_src_dir.set(0)
        self._toggle_buttons()

    def set_use_src_dir(self):
        pdf_file = self.pdf_file.get()
        use_src_dir = self.use_src_dir.get()
        if pdf_file and use_src_dir:
            pdf_path = Path(pdf_file)
            rotated_pdf_path = f'{pdf_path.parent / pdf_path.stem}-rotated.pdf'
            self.rotated_pdf_file.set(rotated_pdf_path)
        self._toggle_buttons()

    def process(self):
        pass

    def _toggle_buttons(self):
        pdf_file = self.pdf_file.get()
        rotated_pdf_file = self.rotated_pdf_file.get()
        if pdf_file and rotated_pdf_file:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'
