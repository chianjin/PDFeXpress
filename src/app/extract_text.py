import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory

import fitz

from utility import get_treeview_file_list
from widget import FileList, Process, FrameTitle, OutputFolder


class ExtractText(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('Extract Text'))
        self.FrameTitle.pack(fill='x', padx=4, pady=4)

        self.FileList = FileList(master=self)
        self.FileList.pack(expand=True, fill='both', padx=4, pady=4)
        self.FileList.configure(text=_('PDF File List'))

        self.OutputFolder = OutputFolder(master=self)
        self.OutputFolder.configure(text=_('Text Output Folder'))
        self.OutputFolder.pack(fill='x', padx=4, pady=4)
        self.OutputFolder.ButtonOutputFolder.configure(command=self.set_output_folder)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Extract Text'))
        self.Process.ButtonProcess.configure(text=_('Extract'), command=self.extract_text)
        self.Process.pack(fill='x', padx=4, pady=4)

    def set_output_folder(self):
        initial_dir = None
        current_folder = self.OutputFolder.output_folder.get()
        if current_folder:
            initial_dir = Path(current_folder)
        else:
            item_list = self.FileList.TreeviewFilelist.get_children()
            if item_list:
                current_file = self.FileList.TreeviewFilelist.item(item_list[0])['text']
                initial_dir = Path(current_file).parent
        folder = askdirectory(
            title=_('Select Text Output Folder'),
            initialdir=initial_dir
        )
        if folder:
            self.OutputFolder.output_folder.set(Path(folder))

    def extract_text(self):
        file_list = get_treeview_file_list(self.FileList.TreeviewFilelist)
        if not file_list:
            return None
        output_folder = self.OutputFolder.output_folder.get()
        if not output_folder:
            return None

        self.Process.ProgressBar.grab_set()
        self.Process.process.set(0)
        self.Process.ProgressBar.configure(maximum=len(file_list))
        for i, input_file in enumerate(file_list, start=1):
            text = []
            output_file = Path(output_folder) / f'{Path(input_file).stem}.txt'
            with fitz.Document(input_file) as input_pdf:
                for page in input_pdf:
                    text.append(page.get_text())
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(''.join(text))
            self.Process.process.set(i)
            self.Process.ProgressBar.update_idletasks()
        self.Process.ProgressBar.grab_release()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Extract Text')
    extract_text = ExtractText(root)
    extract_text.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
