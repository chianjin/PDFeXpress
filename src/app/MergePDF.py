from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_PDF
from ui.UiMergePDF import UiMergePDF
from utils import treeview_add_files, treeview_get_file_list, treeview_get_first_file, treeview_move_item, \
    treeview_remove_items


class MergePDF(UiMergePDF):
    def __init__(self, master=None, **kw):
        super(MergePDF, self).__init__(master, **kw)
        self.TreeViewPDFList['show'] = 'headings'
        self._pdf_count = 0
        self._merged_pdf_file: Union[Path, str] = ''

        self.TreeViewPDFList.configure(yscrollcommand=self.ScrollbarPDFList.set)
        self.ScrollbarPDFList.configure(command=self.TreeViewPDFList.yview)

    def add_pdf(self):
        treeview_add_files(self.TreeViewPDFList, title='选择 PDF 文件', filetypes=FILE_TYPES_PDF)
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

    def set_merged_pdf_file(self):
        if self._merged_pdf_file:
            initial_file = self._merged_pdf_file.name
        else:
            initial_file = treeview_get_first_file(self.TreeViewPDFList)
            if initial_file:
                initial_file = initial_file.with_suffix('.Merged.pdf')
                initial_file = initial_file.name
        merged_pdf_file = asksaveasfilename(
                title='选择合并 PDF 文件名',
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                initialfile=initial_file
                )
        if merged_pdf_file:
            self._merged_pdf_file = Path(merged_pdf_file)
            self.merged_pdf_file.set(self._merged_pdf_file)

        self._toggle_buttons()

    def process(self):
        pdf_list = treeview_get_file_list(self.TreeViewPDFList)
        queue = Queue()
        sub_process = Process(target=merge_pdf, args=(queue, pdf_list, self._merged_pdf_file))
        sub_process_list = [sub_process]
        sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=self._pdf_count)

    def _set_app_info(self):
        self._pdf_count = len(self.TreeViewPDFList.get_children())
        info = f'共 {self._pdf_count} 个 PDF 文件' if self._pdf_count else ''
        self.app_info.set(info)

    def _toggle_buttons(self):
        if self._pdf_count > 1 and self._merged_pdf_file:
            self.ButtonProcess.configure(state='normal')
        else:
            self.ButtonProcess.configure(state='disabled')


def merge_pdf(queue: Queue, pdf_list: list[Path], merged_pdf_file: Path):
    with fitz.Document() as merged_pdf:
        for pdf_no, pdf_file in enumerate(pdf_list, start=1):
            with fitz.Document(str(pdf_file)) as pdf:
                merged_pdf.insert_pdf(pdf)
            queue.put(pdf_no)
        merged_pdf.save(merged_pdf_file)
