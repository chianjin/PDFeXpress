from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import asksaveasfilename
from typing import Union

from app.Progress import Progress
from constants import FILE_TYPES_IMAGE, FILE_TYPES_PDF
from modules import images2pdf
from ui.UiImages2PDF import UiImages2PDF
from utils import treeview_add_files, treeview_get_file_list, \
    treeview_move_item, treeview_remove_items, treeview_get_first_file


class Images2PDF(UiImages2PDF):
    def __init__(self, master=None, **kw):
        super(Images2PDF, self).__init__(master, **kw)
        self.TreeViewImageList['show'] = 'headings'
        self._image_count = 0
        self._pdf_file: Union[str, Path] = ''

        self.TreeViewImageList.configure(yscrollcommand=self.ScrollbarImagesList.set)
        self.ScrollbarImagesList.configure(command=self.TreeViewImageList.yview)

    def add_images(self):
        treeview_add_files(self.TreeViewImageList, title='选择图像文件', filetypes=FILE_TYPES_IMAGE)
        self._set_app_info()
        self._toggle_buttons()

    def remove_images(self):
        treeview_remove_items(self.TreeViewImageList)
        self._set_app_info()
        self._toggle_buttons()

    def remove_all(self):
        treeview_remove_items(self.TreeViewImageList, remove_all=True)
        self._set_app_info()
        self._toggle_buttons()

    def move_top(self):
        treeview_move_item(self.TreeViewImageList, 'top')

    def move_up(self):
        treeview_move_item(self.TreeViewImageList, 'up')

    def move_down(self):
        treeview_move_item(self.TreeViewImageList, 'down')

    def move_bottom(self):
        treeview_move_item(self.TreeViewImageList, 'bottom')

    def set_pdf_file(self):
        if self._pdf_file:
            initial_file = self._pdf_file.name
        else:
            initial_file = treeview_get_first_file(self.TreeViewImageList)
            if initial_file:
                initial_file = initial_file.with_suffix('.pdf')
                initial_file = initial_file.name
        pdf_file = asksaveasfilename(
                filetypes=FILE_TYPES_PDF,
                defaultextension='.pdf',
                title='选择输出文件名',
                initialfile=initial_file
                )
        if pdf_file:
            self._pdf_file = Path(pdf_file)
            self.pdf_file.set(self._pdf_file)

        self._toggle_buttons()

    def process(self):
        image_list = treeview_get_file_list(self.TreeViewImageList)
        queue = Queue()
        sub_process = Process(
                target=images2pdf,
                args=(queue, image_list, self._pdf_file)
                )
        sub_process_list = [sub_process]
        sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=len(image_list))

    def _set_app_info(self):
        self._image_count = len(self.TreeViewImageList.get_children())
        if self._image_count:
            info = f'共 {self._image_count} 个图像文件。'
        else:
            info = ''
        self.process_info.set('')
        self.app_info.set(info)

    def _toggle_buttons(self):
        if self._image_count > 0 and self._pdf_file:
            self.ButtonProcess.configure(state='normal')
        else:
            self.ButtonProcess.configure(state='disabled')
