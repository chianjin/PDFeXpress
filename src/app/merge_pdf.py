import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo

import fitz
import tkinterdnd2

from constant import FILE_WILDCARD
from utility import get_treeview_file_list, drop_pdf_files_to_treeview
from widget import FileListOrdered, OutputFile, Process, FrameTitle


class MergePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('Merge PDF'))

        self.FileList = FileListOrdered(master=self)

        self.Options = Options(master=self)

        self.OutputFile = OutputFile(master=self)
        self.OutputFile.configure(text=_('Output PDF File'))
        self.OutputFile.ButtonOutputFile.configure(command=self.set_output_file)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Merge PDF'))
        self.Process.ButtonProcess.configure(text=_('Merge'), command=self.merge_pdf)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        drop_pdf_files_to_treeview(self.FileList.TreeviewFilelist, event)

    def set_output_file(self):
        initial_dir = None
        initial_file = None
        current_file = self.OutputFile.output_file.get()
        if current_file:
            initial_dir = Path(current_file).parent
            initial_file = Path(current_file).name
        else:
            item_list = self.FileList.TreeviewFilelist.get_children()
            if item_list:
                current_file = self.FileList.TreeviewFilelist.item(item_list[0])['text']
                initial_dir = Path(current_file).parent
                initial_file = f'{Path(current_file).stem}-merged.pdf'
        file = asksaveasfilename(
            title=_('Select PDF Output File'),
            filetypes=FILE_WILDCARD['pdf'],
            defaultextension='.pdf',
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if file:
            self.OutputFile.output_file.set(Path(file))

    def merge_pdf(self):
        file_list = get_treeview_file_list(self.FileList.TreeviewFilelist)
        if len(file_list) < 2:
            return None
        output_file = self.OutputFile.output_file.get()
        if not output_file:
            return None

        self.Process.ProgressBar.grab_set()
        self.Process.process.set(0)
        self.Process.ProgressBar.configure(maximum=len(file_list))
        toc_items = []
        page_count = 1
        with fitz.Document() as out_pdf:
            for i, input_file in enumerate(file_list, start=1):
                with fitz.Document(input_file) as input_pdf:
                    toc_items.append((1, Path(input_file).stem, page_count))
                    page_count += input_pdf.page_count
                    out_pdf.insert_pdf(input_pdf)
                self.Process.process.set(i)
                self.Process.update_idletasks()
            if self.Options.generate_toc.get():
                out_pdf.set_toc(toc_items)
            out_pdf.save(output_file, garbage=4, deflate=True)
        self.Process.ProgressBar.grab_release()
        showinfo(title=_('Done'), message=_('Merge Completed.'))
        self.Process.process.set(0)


class Options(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.generate_toc = tk.BooleanVar(value=True)
        self.CheckButtonTOC = ttk.Checkbutton(
            self,
            variable=self.generate_toc,
            text=_('Generate TOC')
        )
        self.CheckButtonTOC.pack(side='left', padx=4, pady=4)

        self.configure(text=_('Options'))
        self.pack(fill='x', padx=4, pady=4)


if __name__ == '__main__':
    # root = tk.Tk()
    root = tkinterdnd2.Tk()
    root.title('Merge PDF')
    merge_pdf = MergePDF(root)
    merge_pdf.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
