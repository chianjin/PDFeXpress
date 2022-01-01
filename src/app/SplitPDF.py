import math
from itertools import zip_longest
from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import showerror
from typing import Union

import fitz

from app.Progress import Progress
from constants import FILE_TYPES_PDF
from modules import split_pdf
from ui.UiSplitPDF import UiSplitPDF


class SplitPDF(UiSplitPDF):
    def __init__(self, master=None, **kw):
        super(SplitPDF, self).__init__(master, **kw)

        self._page_count = 0
        # string width of page number
        self._page_no_width = 1
        self._pdf_file: Union[str, Path] = ''
        self._split_pdf_dir: Union[str, Path] = ''
        self._split_mode = self.split_mode.get()
        self._use_src_dir = 0
        self.use_src_dir.set(self._use_src_dir)

    def get_pdf_file(self):
        old_pdf_file = self._pdf_file
        self._pdf_file = askopenfilename(title='选择 PDF 文件', filetypes=FILE_TYPES_PDF)
        if self._pdf_file:
            self._pdf_file = Path(self._pdf_file)
            if old_pdf_file != self._pdf_file:
                self.pdf_file.set(self._pdf_file)
                self.set_use_src_dir()
                with fitz.Document(str(self._pdf_file)) as pdf:
                    self._page_count = pdf.page_count
                # Set split options
                # Pages per split pdf in page split mode
                self.split_page.set(2)
                # Count of split pdf in count split mode
                self._set_split_count()
                # First page number of split pdf in range split mode
                self.split_range_start.set(1)
                # Last page number of split pdf in range split mode
                self.split_range_stop.set(self._page_count)
                # Width of split pdf suffix page number
                self._page_no_width = len(str(self._page_count))
                self.app_info.set(f'共 {self._page_count} 页。')
                self.process_info.set('')
                self._toggle_buttons()

    def set_split_pdf_dir(self):
        old_split_pdf_dir = self._split_pdf_dir
        self._split_pdf_dir = askdirectory(title='选择分割 PDF 文件保存目录', mustexist=True)
        if self._split_pdf_dir:
            self._split_pdf_dir = Path(self._split_pdf_dir)
            if old_split_pdf_dir != self._split_pdf_dir:
                self.split_pdf_dir.set(self._split_pdf_dir)
                if self._split_pdf_dir:
                    if self._split_pdf_dir == self._pdf_file.parent:
                        self._use_src_dir = 1
                    else:
                        self._use_src_dir = 0
                self.use_src_dir.set(self._use_src_dir)
                self.process_info.set('')
                self._toggle_buttons()

    def set_split_mode(self):
        self._split_mode = self.split_mode.get()
        self.process_info.set('')
        if self._split_mode == 'single':
            self.EntrySplitPage.configure(state='disabled')
            self.ComboboxSplitCount.configure(state='disabled')
            self.EntrySplitRangeStart.configure(state='disabled')
            self.EntrySplitRangeStop.configure(state='disabled')
        elif self._split_mode == 'page':
            self.EntrySplitPage.configure(state='normal')
            self.ComboboxSplitCount.configure(state='disabled')
            self.EntrySplitRangeStart.configure(state='disabled')
            self.EntrySplitRangeStop.configure(state='disabled')
        elif self._split_mode == 'count':
            self.EntrySplitPage.configure(state='disable')
            self.ComboboxSplitCount.configure(state='readonly')
            self.split_count.set(2)
            self.EntrySplitRangeStart.configure(state='disabled')
            self.EntrySplitRangeStop.configure(state='disabled')
        elif self._split_mode == 'range':
            self.EntrySplitPage.configure(state='disabled')
            self.ComboboxSplitCount.configure(state='disabled')
            self.EntrySplitRangeStart.configure(state='normal')
            self.split_range_start.set(1)
            self.EntrySplitRangeStop.configure(state='normal')
            self.split_range_stop.set(self._page_count)

    def valid_page(self):
        pages = self.EntrySplitPage.get()
        if pages.isdigit() and 1 < int(pages) < self._page_count:
            return True
        else:
            showerror(title='错误', message=f'请输入介于 2 与 {self._page_count} 之间的整数。')
            self.EntrySplitPage.focus()
            return False

    def valid_start(self):
        start = self.EntrySplitRangeStart.get()
        if start.isdigit() and 1 <= int(start) <= self._page_count:
            return True
        else:
            showerror(title='错误', message=f'请输入 1 到 {self._page_count} 的整数')
            self.EntrySplitRangeStart.focus()
            return False

    def valid_stop(self):
        stop = self.EntrySplitRangeStop.get()
        if stop.isdigit() and 1 <= int(stop) <= self._page_count:
            return True
        else:
            showerror(title='错误', message=f'请输入 1 到 {self._page_count} 的整数')
            self.EntrySplitRangeStop.focus()
            return False

    def set_use_src_dir(self):
        old_split_pdf_dir = self._split_pdf_dir
        self._use_src_dir = self.use_src_dir.get()
        if self._pdf_file and self._use_src_dir:
            self._split_pdf_dir = self._pdf_file.parent
            if old_split_pdf_dir != self._split_pdf_dir:
                self.split_pdf_dir.set(self._split_pdf_dir)
                self.process_info.set('')
                self._toggle_buttons()

    def process(self):
        if self._split_mode == 'range':
            split_range_list = ((self.split_range_start.get() - 1, self.split_range_stop.get() - 1),)
        elif self._split_mode in ('page', 'count'):
            if self._split_mode == 'page':
                range_size = self.split_page.get()
            else:
                range_size = math.ceil(self._page_count / self.split_count.get())
            start_range = range(self._page_count)[::range_size]
            stop_range = range(self._page_count)[range_size - 1::range_size]
            split_range_list = tuple(zip_longest(start_range, stop_range))
        else:
            split_range_list = tuple(zip(range(self._page_count), range(self._page_count)))

        queue = Queue()
        sub_process = Process(
                target=split_pdf,
                args=(queue, self._pdf_file, self._split_pdf_dir, self._split_mode, split_range_list)
                )
        sub_process_list = [sub_process]
        sub_process.start()
        Progress(process_list=sub_process_list, queue=queue, maximum=len(split_range_list))

    def _set_split_count(self):
        """Set valid values of count in count split mod"""
        count = list(set([math.ceil(self._page_count / p) for p in range(2, self._page_count)]))
        count.sort()
        count = [str(a) for a in count]
        values = ' '.join(count)
        self.ComboboxSplitCount.configure(values=values)

    def _toggle_buttons(self):
        pdf_file = self.pdf_file.get()

        if pdf_file:
            self.RadiobuttonSplitSingle.configure(state='normal')
            self.RadiobuttonSplitPage.configure(state='normal')
            self.LabelSplitPageUnit.configure(state='normal')
            self.RadiobuttonSplitCount.configure(state='normal')
            self.LabelSplitCountUnit.configure(state='normal')
            self.RadiobuttonSplitRange.configure(state='normal')
            self.LabelSplitRangeTo.configure(state='normal')
            self.LabelSplitRangeUnit.configure(state='normal')

        split_pdf_dir = self.split_pdf_dir.get()

        if pdf_file and split_pdf_dir:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'
