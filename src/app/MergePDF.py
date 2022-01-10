from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_PDF, TRANSLATER as _
from ui.UiMergePDF import UiMergePDF
from utils import check_dir, check_file_exist, treeview_add_files, treeview_get_file_list, treeview_get_first_file, \
    treeview_move_item, treeview_remove_items


class MergePDF(UiMergePDF):
    def __init__(self, master=None, **kw):
        super(MergePDF, self).__init__(master, **kw)

        self.LabelFrameName.configure(text=_('Merge PDF'))
        self.FramePDFList.configure(text=_('PDF List'))
        self.ButtonAddPDF.configure(text=_('Add PDF'))
        self.ButtonRemovePDF.configure(text=_('Remove PDF'))
        self.ButtonRemoveAll.configure(text=_('Remove All'))
        self.ButtonMoveTop.configure(text=_('Move to First'))
        self.ButtonMoveUp.configure(text=_('Move Up'))
        self.ButtonMoveDown.configure(text=_('Move Down'))
        self.ButtonMoveBottom.configure(text=_('Move to Last'))
        self.FrameMergedPDFFile.configure(text=_('Merged PDF File'))
        self.ButtonMergedPDFFile.configure(text=_('Browser'))
        self.FrameProcess.configure(text=_('Images to PDF'))
        self.ButtonProcess.configure(text=_('Convert'))

        self.TreeViewPDFList.heading('ColumnDirName', anchor='w', text=_('Folder'))
        self.TreeViewPDFList.heading('ColumnFileName', anchor='w', text=_('File Name'))

        self.TreeViewPDFList['show'] = 'headings'
        self._pdf_count = 0
        self._merged_pdf_file: Union[Path, str] = ''

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

    def set_merged_pdf_file(self):
        if self._merged_pdf_file:
            initial_file = self._merged_pdf_file.name
        else:
            initial_file = treeview_get_first_file(self.TreeViewPDFList)
            if initial_file:
                initial_file = initial_file.with_suffix('.Merged.pdf')
                initial_file = initial_file.name
        merged_pdf_file = asksaveasfilename(
                title=_('Select merged PDF file'),
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
        for pdf_file in pdf_list:
            if not check_file_exist(pdf_file):
                return None
        check_dir(self._merged_pdf_file.parent)

        queue = Queue()
        sub_process = Process(target=merge_pdf, args=(queue, pdf_list, self._merged_pdf_file))
        sub_process_list = [sub_process]
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
