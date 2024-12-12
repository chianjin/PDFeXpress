from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename

import fitz
import tkinterdnd2

from constant import FILE_WILDCARD
from utility import get_treeview_file_list, split_drop_data, add_files_to_treeview
from widget import FileListOrdered, OutputFile, Process, FrameTitle


class MergePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.Title = FrameTitle(master=self, frame_title=_('Merge PDF'))
        self.Title.pack(fill='x', padx=4, pady=4)

        self.FileList = FileListOrdered(master=self)
        self.FileList.pack(expand=True, fill='both', padx=4, pady=4)
        self.FileList.configure(text=_('PDF File List'))

        self.OutputFile = OutputFile(master=self)
        self.OutputFile.configure(text=_('Output PDF File'))
        self.OutputFile.pack(fill='x', padx=4, pady=4)
        self.OutputFile.ButtonOutputFile.configure(command=self.set_output_file)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Merge PDF'))
        self.Process.ButtonProcess.configure(text=_('Merge'), command=self.merge_pdf)
        self.Process.pack(fill='x', padx=4, pady=4)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        file_list = split_drop_data(event.data)
        file_list = [file for file in file_list if file.suffix.lower() == '.pdf']
        add_files_to_treeview(self.FileList.TreeviewFilelist, file_list)

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
        with fitz.Document() as out_pdf:
            for i, input_file in enumerate(file_list, start=1):
                with fitz.Document(input_file) as input_pdf:
                    out_pdf.insert_pdf(input_pdf)
                self.Process.process.set(i)
                self.Process.update_idletasks()
            out_pdf.save(output_file)
        self.Process.ProgressBar.grab_release()


if __name__ == '__main__':
    # root = tk.Tk()
    root = tkinterdnd2.Tk()
    root.title('Merge PDF')
    merge_pdf = MergePDF(root)
    merge_pdf.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
