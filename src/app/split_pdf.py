import math
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
from turtledemo.penrose import start

import fitz

from constant import FILE_WILDCARD
from widget import Process, FrameTitle, OutputFolder, InputFile


class SplitPDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('Split PDF'))
        self.FrameTitle.pack(fill='x', padx=4, pady=4)

        self.InputFile = InputFile(master=self)
        self.InputFile.pack(fill='x', padx=4, pady=4)
        self.InputFile.ButtonInputFile.configure(command=self.add_file)

        self.Options = Options(master=self)
        self.Options.pack(fill='x', padx=4, pady=4)

        self.OutputFolder = OutputFolder(master=self)
        self.OutputFolder.configure(text=_('PDF Output Folder'))
        self.OutputFolder.pack(fill='x', padx=4, pady=4)
        self.OutputFolder.ButtonOutputFolder.configure(command=self.set_output_folder)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Split PDF'))
        self.Process.ButtonProcess.configure(text=_('Split'), command=self.split_pdf)
        self.Process.pack(fill='x', padx=4, pady=4)

    def set_output_folder(self):
        initial_dir = None
        current_folder = self.OutputFolder.output_folder.get()
        if current_folder:
            initial_dir = Path(current_folder)
        else:
            input_file = self.InputFile.input_file.get()
            if input_file:
                initial_dir = Path(input_file).parent
        folder = askdirectory(
            title=_('Select PDF Output Folder'),
            initialdir=initial_dir
        )
        if folder:
            self.OutputFolder.output_folder.set(Path(folder))

    def split_pdf(self):
        input_file = self.InputFile.input_file.get()
        if not input_file:
            return None
        output_folder = self.OutputFolder.output_folder.get()
        if not output_folder:
            return None
        self.Process.ProgressBar.grab_set()
        self.Process.process.set(0)
        with fitz.Document(input_file) as input_pdf:
            page_width = len(str(input_pdf.page_count))
            split_range = self._generate_split_range(input_pdf.page_count)
            self.Process.ProgressBar.configure(maximum=len(split_range))
            for i, page_range in enumerate(split_range, start=1):
                from_page, to_page = page_range
                if to_page > input_pdf.page_count:
                    to_page = input_pdf.page_count
                if self.Options.split_mode.get() == 'single_page':
                    output_file = f'{output_folder}/{Path(input_file).stem}-P{from_page:0{page_width}d}.pdf'
                else:
                    output_file = f'{output_folder}/{Path(input_file).stem}-P{from_page:0{page_width}d}-{to_page:0{page_width}d}.pdf'
                with fitz.Document() as out_pdf:
                    out_pdf.insert_pdf(input_pdf, from_page=from_page, to_page=to_page)
                    out_pdf.save(output_file)
                self.Process.process.set(i)
                self.Process.ProgressBar.update()
        self.Process.ProgressBar.grab_release()

    def _generate_split_range(self, page_count):
        mode = self.Options.split_mode.get()
        if mode in ('single_page', 'by_pages', 'by_count'):
            if mode == 'single_page':
                step = 1
            elif mode == 'by_pages':
                step = self.Options.pages.get()
            else:
                step = math.ceil(page_count / self.Options.count.get())
            return [(i, i + step - 1) for i in range(1, page_count + 1, step)]
        elif mode == 'by_range':
            return [(self.Options.range_start.get(), self.Options.range_end.get())]

    def add_file(self):
        file = askopenfilename(
            title=_('Select PDF File'),
            filetypes=FILE_WILDCARD['pdf']
        )
        if file:
            self.InputFile.input_file.set(Path(file))
            with fitz.Document(file) as input_pdf:
                self.Options.range_end.set(input_pdf.page_count)

class Options(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.split_mode = tk.StringVar(value='single_page')
        self.RadioButtonSinglePage = ttk.Radiobutton(
            master=self,
            text=_('Single Page'),
            variable=self.split_mode,
            value='single_page'
        )
        self.RadioButtonSinglePage.pack(side='left', padx=4, pady=4)
        self.RadioButtonByPages = ttk.Radiobutton(
            master=self,
            text=_('By Pages'),
            variable=self.split_mode,
            value='by_pages'
        )
        self.RadioButtonByPages.pack(side='left', padx=4, pady=4)
        self.pages = tk.IntVar(value=2)
        self.EntryPages = ttk.Entry(master=self, width=4, justify='center', textvariable=self.pages)
        self.EntryPages.pack(side='left', padx=4, pady=4)
        self.RadioButtonByCount = ttk.Radiobutton(
            master=self,
            text=_('By Count'),
            variable=self.split_mode,
            value='by_count'
        )
        self.RadioButtonByCount.pack(side='left', padx=4, pady=4)
        self.count = tk.IntVar(value=2)
        self.EntryCount = ttk.Entry(master=self, width=4, justify='center', textvariable=self.count)
        self.EntryCount.pack(side='left', padx=4, pady=4)
        self.RadioButtonByRange = ttk.Radiobutton(
            master=self,
            text=_('By Range'),
            variable=self.split_mode,
            value='by_range'
        )
        self.RadioButtonByRange.pack(side='left', padx=4, pady=4)
        self.range_start = tk.IntVar(value=1)
        self.range_end = tk.IntVar(value=1)
        self.EntryStart = ttk.Entry(master=self, width=4, justify='center', textvariable=self.range_start)
        self.EntryStart.pack(side='left', padx=4, pady=4)
        label_to = ttk.Label(master=self, text='-')
        label_to.pack(side='left', pady=4)
        self.EntryEnd = ttk.Entry(master=self, width=4, justify='center', textvariable=self.range_end)
        self.EntryEnd.pack(side='left', padx=4, pady=4)

        self.configure(text=_('Options'))
        self.pack(fill='x', padx=4, pady=4)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Split PDF')
    split_pdf = SplitPDF(root)
    split_pdf.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()