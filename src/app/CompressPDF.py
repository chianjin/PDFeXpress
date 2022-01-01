import os.path
from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename

import fitz

from constants import FILE_TYPES_PDF
from ui.UiCompressPDF import UiCompressPDF
from utils import int2byte_unit


class CompressPDF(UiCompressPDF):
    def __init__(self, master=None, **kw):
        super(CompressPDF, self).__init__(master, **kw)
        self.image_quality.set(80)
        self.image_dpi.set(144)
        self.use_src_dir.set(0)

    def get_pdf_file(self):
        pdf_file = askopenfilename(filetypes=FILE_TYPES_PDF, title='选择 PDF 文件')
        if pdf_file:
            pdf_path = Path(pdf_file)
            self.pdf_file.set(pdf_path)
            self.set_use_src_dir()
            file_size = int2byte_unit(os.path.getsize(pdf_file))
            self.pdf_info.set(f'原文件大小 {file_size}。')

    def set_compressed_pdf_file(self):
        pdf_file = self.pdf_file.get()
        pdf_path = Path(pdf_file)
        compressed_pdf_filename = f'{pdf_path.stem}-compressed.pdf' if pdf_file else ''
        compressed_pdf_file = asksaveasfilename(
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                title='选择输出文本文件名',
                initialfile=compressed_pdf_filename
                )
        if compressed_pdf_file:
            self.compressed_pdf_file.set(Path(compressed_pdf_file))
            self.use_src_dir.set(0)
        self._toggle_buttons()

    def set_image_quality(self, scale_value):
        value = int(round(float(scale_value) * 2, -1)) // 2  # Scale step: 5
        self.image_quality.set(value)

    def set_use_src_dir(self):
        pdf_file = self.pdf_file.get()
        use_src_dir = self.use_src_dir.get()
        if pdf_file and use_src_dir:
            pdf_path = Path(pdf_file)
            text_path = f'{pdf_path.parent / pdf_path.stem}-compressed.pdf'
            self.compressed_pdf_file.set(text_path)
        self._toggle_buttons()

    def process(self):
        pdf_file = self.pdf_file.get()
        compressed_pdf_file = self.compressed_pdf_file.get()
        compressed_mode = self.compress_mode.get()
        image_quality = self.image_quality.get()
        image_dpi = self.image_dpi.get()
        if compressed_mode == 'image':
            self._compress_image(pdf_file, compressed_pdf_file, image_quality, image_dpi)
        else:
            self._compress_page(pdf_file, compressed_pdf_file, image_quality, image_dpi)

    def _compress_image(self, input_pdf, output_pdf, image_quality, image_dpi):
        pass

    def _compress_page(self, input_pdf, output_pdf, image_quality, image_dpi):
        zoom = image_dpi // 96
        matrix = fitz.Matrix(zoom, zoom)
        with fitz.Document(input_pdf) as in_pdf:
            with fitz.Document() as out_pdf:
                for in_page in in_pdf:
                    in_page.get_pixmap(matrix=matrix)

    def _toggle_buttons(self):
        pdf_file = self.pdf_file.get()
        compressed_pdf_file = self.compressed_pdf_file.get()
        if pdf_file and compressed_pdf_file:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'
