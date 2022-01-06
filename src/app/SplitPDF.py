import math
from itertools import zip_longest
from multiprocessing import Process, Queue
from pathlib import Path
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from typing import Union

import fitz

from app.Progress import Progress
from ui.UiSplitPDF import UiSplitPDF
from utils import get_pdf_info, check_dir, check_file_exist


class SplitPDF(UiSplitPDF):
    def __init__(self, master=None, **kw):
        super(SplitPDF, self).__init__(master, **kw)

        self._page_count = 0
        # string width of page number
        self._page_no_width = 1
        self._pdf_file: Union[str, Path] = ''
        self._split_pdf_dir: Union[str, Path] = ''
        self._split_mode = self.split_mode.get()

    def get_pdf_file(self):
        self._pdf_file, self._page_count, self._page_no_width = get_pdf_info()
        if self._page_count > 0:
            self.pdf_file.set(self._pdf_file)
            self.app_info.set(f'共 {self._page_count} 页')
            self._split_pdf_dir = self._pdf_file.parent
            self.split_pdf_dir.set(self._split_pdf_dir)

            # Set split options
            # Pages per split pdf in page split mode
            self.split_page.set(2)
            # Count of split pdf in count split mode
            self._set_split_count()
            # First page number of split pdf in range split mode
            self.split_range_start.set(1)
            # Last page number of split pdf in range split mode
            self.split_range_stop.set(self._page_count)

        self._toggle_buttons()

    def set_split_pdf_dir(self):
        self._split_pdf_dir = askdirectory(title='选择图像输出目录')
        if self._split_pdf_dir:
            self._split_pdf_dir = Path(self._split_pdf_dir)
            self.split_pdf_dir.set(self._split_pdf_dir)
        self._toggle_buttons()

    def set_split_mode(self):
        if self._pdf_file:
            self._split_mode = self.split_mode.get()
            if self._split_mode == 'page':
                self.EntrySplitPage.configure(state='normal')
                self.ComboboxSplitCount.configure(state='disabled')
                self.EntrySplitRangeStart.configure(state='disabled')
                self.EntrySplitRangeStop.configure(state='disabled')
            elif self._split_mode == 'count':
                self.EntrySplitPage.configure(state='disable')
                self.ComboboxSplitCount.configure(state='readonly')
                self.EntrySplitRangeStart.configure(state='disabled')
                self.EntrySplitRangeStop.configure(state='disabled')
            elif self._split_mode == 'range':
                self.EntrySplitPage.configure(state='disabled')
                self.ComboboxSplitCount.configure(state='disabled')
                self.EntrySplitRangeStart.configure(state='normal')
                self.EntrySplitRangeStop.configure(state='normal')
        else:
            self._split_mode = 'single'
            self.split_mode.set(self._split_mode)
            self.EntrySplitPage.configure(state='disabled')
            self.ComboboxSplitCount.configure(state='disabled')
            self.EntrySplitRangeStart.configure(state='disabled')
            self.EntrySplitRangeStop.configure(state='disabled')

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

    def process(self):
        if not check_file_exist(self._pdf_file):
            return None
        check_dir(self._split_pdf_dir)

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
        progress = Progress(process_list=sub_process_list, queue=queue, maximum=len(split_range_list))
        self.wait_window(progress)

    def _set_split_count(self):
        """Set valid values of count in count split mod"""
        count = list(set([math.ceil(self._page_count / p) for p in range(2, self._page_count)]))
        count.sort()
        count = [str(a) for a in count]
        values = ' '.join(count)
        self.ComboboxSplitCount.configure(values=values)
        self.ComboboxSplitCount.set(2)

    def _toggle_buttons(self):
        if self._pdf_file and self._page_count > 1:
            self.RadiobuttonSplitSingle.configure(state='normal')
            self.RadiobuttonSplitPage.configure(state='normal')
            self.LabelSplitPageUnit.configure(state='normal')
            self.RadiobuttonSplitCount.configure(state='normal')
            self.LabelSplitCountUnit.configure(state='normal')
            self.RadiobuttonSplitRange.configure(state='normal')
            self.LabelSplitRangeTo.configure(state='normal')
            self.LabelSplitRangeUnit.configure(state='normal')

        if self._pdf_file and self._page_count > 1 and self._split_pdf_dir:
            self.ButtonProcess['state'] = 'normal'
        else:
            self.ButtonProcess['state'] = 'disabled'


def split_pdf(
        queue: Queue, pdf_file: Union[str, Path, None], split_pdf_dir: Union[str, Path], split_mode: str,
        split_range_list: tuple[tuple[int]]
        ):
    count = 0
    with fitz.Document(pdf_file) as pdf:
        page_no_width = len(str(pdf.page_count))
        for start, stop in split_range_list:
            if split_mode == 'single':
                _split_pdf_file = f'{split_pdf_dir / pdf_file.stem}-split-P{start + 1:0{page_no_width}d}.pdf'
            else:
                if not stop:
                    stop = pdf.page_count - 1
                _split_pdf_file = f'{split_pdf_dir / pdf_file.stem}-split-' \
                                  f'P{start + 1:0{page_no_width}d}-{stop + 1:0{page_no_width}d}.pdf'

            with fitz.Document() as _split_pdf:
                _split_pdf.insert_pdf(pdf, from_page=start, to_page=stop)
                _split_pdf.save(_split_pdf_file)
            count += 1
            queue.put(count)
