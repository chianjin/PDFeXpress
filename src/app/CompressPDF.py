import os.path
import math
from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

from constants import FILE_TYPES_PDF, PHYSICAL_CPU_COUNT
from modules import compress_pdf, merge_compressed_pdf
from app.Progress import Progress
from ui.UiCompressPDF import UiCompressPDF
from utils import int2byte_unit, get_pdf_info


class CompressPDF(UiCompressPDF):
    def __init__(self, master=None, **kw):
        super(CompressPDF, self).__init__(master, **kw)
        self._pdf_file: Union[str, Path] = ''
        self._page_count = 0
        self._compressed_pdf_file: Union[str, Path] = ''
        self._image_quality = 75
        self._max_dpi = 144
        self.image_quality.set(self._image_quality)
        self.image_dpi.set(self._max_dpi)

    def get_pdf_file(self):
        self._pdf_file, self._page_count, _ = get_pdf_info()
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            file_size = int2byte_unit(os.path.getsize(self._pdf_file))
            self.pdf_info.set(f'共 {self._page_count} 页  {file_size}')
            self._compressed_pdf_file = self._pdf_file.with_suffix('.Compressed.pdf')
            self.compressed_pdf_file.set(self._compressed_pdf_file)
        self._toggle_buttons()

    def set_compressed_pdf_file(self):
        if self._compressed_pdf_file:
            initial_file = self._compressed_pdf_file.name
        else:
            initial_file = ''
        rotated_pdf_file = asksaveasfilename(
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                title='选择旋转的 PDF 文件名',
                initialfile=initial_file
                )
        if rotated_pdf_file:
            self._compressed_pdf_file = Path(rotated_pdf_file)
            self.compressed_pdf_file.set(self._compressed_pdf_file)

        self._toggle_buttons()

    def set_image_quality(self, scale_value):
        value = int(round(float(scale_value) * 2, -1)) // 2  # Scale step: 5
        self._image_quality = value
        self.image_quality.set(self._image_quality)

    def process(self):
        # split pdf range
        page_range_list = []
        process_count = PHYSICAL_CPU_COUNT
        pdf_page_range = list(range(self._page_count))
        while process_count > 0:
            chunk_size = math.ceil(len(pdf_page_range) / process_count)
            page_range_list.append(pdf_page_range[:chunk_size])
            pdf_page_range = pdf_page_range[chunk_size:]
            process_count -= 1
        page_range_list = [page_range for page_range in page_range_list if len(page_range)]

        queue = Queue()
        sub_process_list = []
        for process_id, page_range in enumerate(page_range_list):
            print(page_range)
            sub_process = Process(
                    target=compress_pdf,
                    args=(
                            queue, self._pdf_file, self._compressed_pdf_file, self._image_quality,
                            self._max_dpi, page_range, process_id
                            )
                    )
            sub_process_list.append(sub_process)
        for sub_process in sub_process_list:
            sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=self._page_count)
        # TODO
        #
        sub_process = Process(
                target=merge_compressed_pdf,
                args=(queue, self._compressed_pdf_file, page_range_list)
                )
        sub_process_list = [sub_process]
        sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=len(page_range_list))
        for file_no in range(len(page_range_list)):
            sub_compressed_pdf_file = self._compressed_pdf_file.parent / f'{file_no}-{self._compressed_pdf_file.name}'
            # os.unlink(sub_compressed_pdf_file)

    def _toggle_buttons(self):
        if self._pdf_file and self._compressed_pdf_file:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'
