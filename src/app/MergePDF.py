from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

from app.Progress import Progress
from constants import FILE_TYPES_PDF
from modules import merge_pdf
from ui.UiMergePDF import UiMergePDF
from utils import add_treeview_files, get_treeview_files, move_treeview_item, remove_treeview_items


class MergePDF(UiMergePDF):
    def __init__(self, master=None, **kw):
        super(MergePDF, self).__init__(master, **kw)
        self.TreeViewPDFList['show'] = 'headings'
        self._pdf_count = 0
        self._merged_pdf_file: Union[str, Path] = ''

    def add_pdf(self):
        add_treeview_files(self.TreeViewPDFList, title='选择 PDF 文件', filetypes=FILE_TYPES_PDF)
        self._set_app_info()
        self._toggle_buttons()

    def remove_pdf(self):
        remove_treeview_items(self.TreeViewPDFList)
        self._set_app_info()
        self._toggle_buttons()

    def remove_all(self):
        remove_treeview_items(self.TreeViewPDFList, remove_all=True)
        self._set_app_info()
        self._toggle_buttons()

    def move_top(self):
        move_treeview_item(self.TreeViewPDFList, 'top')

    def move_up(self):
        move_treeview_item(self.TreeViewPDFList, 'up')

    def move_down(self):
        move_treeview_item(self.TreeViewPDFList, 'down')

    def move_bottom(self):
        move_treeview_item(self.TreeViewPDFList, 'bottom')

    def set_merged_pdf_file(self):
        if self._pdf_count:
            item = self.TreeViewPDFList.get_children()[0]
            _dir, pdf_filename = self.TreeViewPDFList.item(item).get('values')
            merged_pdf_filename = f'{Path(pdf_filename).stem}-merged.pdf'
        else:
            merged_pdf_filename = ''
        old_merged_pdf_file = self._merged_pdf_file
        merged_pdf_file = asksaveasfilename(
                title='选择合并 PDF 文件名',
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                initialfile=merged_pdf_filename
                )
        if merged_pdf_file:
            self._merged_pdf_file = Path(merged_pdf_file)
            if old_merged_pdf_file != self._merged_pdf_file:
                self.merged_pdf_file.set(self._merged_pdf_file)
                self._toggle_buttons()

    def process(self):
        pdf_list = get_treeview_files(self.TreeViewPDFList)
        queue = Queue()
        sub_process = Process(target=merge_pdf, args=(queue, pdf_list, self._merged_pdf_file))
        sub_process_list = [sub_process]
        sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=self._pdf_count)

    def _set_app_info(self):
        self._pdf_count = len(self.TreeViewPDFList.get_children())
        info = f'共 {self._pdf_count} 个 PDF 文件。' if self._pdf_count else ''
        self.app_info.set(info)

    def _toggle_buttons(self):
        if self._pdf_count > 1 and self._merged_pdf_file:
            self.ButtonProcess.configure(state='normal')
        else:
            self.ButtonProcess.configure(state='disabled')
