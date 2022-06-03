from typing import Union
from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_PDF, PHYSICAL_CPU_COUNT
from ui.UiRotatePDF import UiRotatePDF
from utils import check_dir, treeview_add_files, treeview_get_file_list, treeview_get_first_file, \
    treeview_move_item, treeview_remove_items


class RotatePDF(UiRotatePDF):
    def __init__(self, master=None, **kw):
        super(RotatePDF, self).__init__(master, **kw)

        self._pdf_count = 0
        self._output_dir: Path | str = self.output_dir.get()
        self._use_source_folder = self.use_source_folder.get()

        self.TreeViewPDFList.configure(yscrollcommand=self.ScrollbarPDFList.set)
        self.ScrollbarPDFList.configure(command=self.TreeViewPDFList.yview)

    def add_pdf(self):
        treeview_add_files(self.TreeViewPDFList, title=_('Select PDF files'), filetypes=FILE_TYPES_PDF)
        self._set_app_info()
        self._toggle_buttons()

    def remove_pdf(self):
        treeview_remove_items(self.TreeViewPDFList)
        self._set_app_info()
        self._toggle_buttons()

    def remove_all(self):
        treeview_remove_items(self.TreeViewPDFList, remove_all=True)
        self._set_app_info()
        self._toggle_buttons()

    def move_top(self):
        treeview_move_item(self.TreeViewPDFList, 'top')

    def move_up(self):
        treeview_move_item(self.TreeViewPDFList, 'up')

    def move_down(self):
        treeview_move_item(self.TreeViewPDFList, 'down')

    def move_bottom(self):
        treeview_move_item(self.TreeViewPDFList, 'bottom')

    def set_output_dir(self):
        self._output_dir = askdirectory(title=_('Select Rotated PDF folder'))
        if self._output_dir:
            self._output_dir = Path(self._output_dir)
            self.output_dir.set(self._output_dir)
            self._use_source_folder = False
            self.use_source_folder.set(self._use_source_folder)
        self._toggle_buttons()

    def set_source_folder(self):
        self._use_source_folder = self.use_source_folder.get()
        if self._use_source_folder:
            self.EntryOutputDir.configure(state='disabled')
            self._output_dir = ''
        else:
            self.EntryOutputDir.configure(state='readonly')
            self._output_dir = self.output_dir.get()
            if not self._output_dir:
                self._output_dir = Path(treeview_get_first_file(self.TreeViewPDFList)).parent
                self.output_dir.set(self._output_dir)

    def process(self):
        if self._output_dir:
            check_dir(Path(self._output_dir))

        pdf_range = treeview_get_file_list(self.TreeViewPDFList)
        pdf_range_list = []

        for start in range(PHYSICAL_CPU_COUNT):
            # if PHYSICAL_CPU_COUNT == 4
            # [0, 4, 8, ...], [1, 5, 9, ...], [2, 6, 10, ...], [3, 7, 11, ...]
            sub_pdf_range = pdf_range[start::PHYSICAL_CPU_COUNT]
            pdf_range_list.append(sub_pdf_range)
        pdf_range_list = [_range for _range in pdf_range_list if len(_range)]

        queue = Queue()
        sub_process_list = []
        for pdf_range in pdf_range_list:
            sub_process = Process(
                    target=rotate_pdf,
                    args=(queue, pdf_range, self._output_dir, self.rotate_degree.get())
                    )
            sub_process_list.append(sub_process)
        for sub_process in sub_process_list:
            sub_process.start()
        progress = Progress(process_list=sub_process_list, queue=queue, maximum=self._pdf_count)
        self.wait_window(progress)

    def _set_app_info(self):
        self._pdf_count = len(self.TreeViewPDFList.get_children())
        if self._pdf_count:
            info = _('Total PDF: {}').format(self._pdf_count)
        else:
            info = ''
        self.app_info.set(info)

    def _toggle_buttons(self):
        if self._pdf_count > 0:
            self.ButtonProcess.configure(state='normal')
        else:
            self.ButtonProcess.configure(state='disabled')


def rotate_pdf(queue: Queue, pdf_list: list, output_dir: Union[str, Path], rotation: int):
    for pdf_file in pdf_list:
        if output_dir:
            rotated_pdf_file = Path(output_dir) / f'{Path(pdf_file).stem}-Rotated.pdf'
        else:
            rotated_pdf_file = Path(pdf_file).parent / f'{Path(pdf_file).stem}-Rotated.pdf'
        with fitz.Document(pdf_file) as pdf:
            for page_no, page in enumerate(pdf):
                page.set_rotation(rotation=rotation)
            pdf.save(rotated_pdf_file)
            queue.put(1)
