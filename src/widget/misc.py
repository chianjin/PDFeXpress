import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from constant import FILE_WILDCARD


class FrameTitle(ttk.Frame):
    def __init__(self, master=None, frame_title='Frame Title', **kw):
        super().__init__(master, **kw)
        self.LabelTitle = ttk.Label(master=self, text=_(frame_title), font=('Microsoft YaHei UI', 24, 'bold'))
        self.LabelTitle.pack(side='left', padx=8, pady=8)


class InputFile(ttk.LabelFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.input_file = tk.StringVar()
        self.EntryInputFile = ttk.Entry(master=self, textvariable=self.input_file, state='readonly')
        self.EntryInputFile.pack(expand=True, side='left', fill='x', padx=4, pady=4)
        self.ButtonInputFile = ttk.Button(
            master=self,
            text=_('Browse'),
            command=self.set_input_file
        )
        self.ButtonInputFile.pack(side='left', padx=4, pady=4)
        self.configure(text=_('PDF File'))

    def set_input_file(self):
        file = askopenfilename(filetypes=FILE_WILDCARD['pdf'])
        if file:
            self.input_file.set(Path(file))


class OutputFile(ttk.LabelFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.output_file = tk.StringVar()
        self.EntryOutputFile = ttk.Entry(master=self, textvariable=self.output_file, state='readonly')
        self.EntryOutputFile.pack(expand=True, side='left', fill='x', padx=4, pady=4)
        self.ButtonOutputFile = ttk.Button(
            master=self,
            text=_('Browse'),
        )
        self.ButtonOutputFile.pack(side='left', padx=4, pady=4)
        self.configure(text=_('Output File'))


class OutputFolder(ttk.LabelFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.output_folder = tk.StringVar()
        self.EntryOutputFolder = ttk.Entry(master=self, textvariable=self.output_folder, state='readonly')
        self.EntryOutputFolder.pack(expand=True, side='left', fill='x', padx=4, pady=4)
        self.ButtonOutputFolder = ttk.Button(
            master=self,
            text=_('Browse'),
        )
        self.ButtonOutputFolder.pack(side='left', padx=4, pady=4)
        self.configure(text=_('Output Folder'))


class Process(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.process = tk.IntVar(value=0)
        self.ProgressBar = ttk.Progressbar(
            master=self,
            orient='horizontal',
            mode='determinate',
            variable=self.process
        )
        self.ProgressBar.pack(side='left', expand=True,fill='x', padx=4, pady=4)
        self.ButtonProcess = ttk.Button(
            master=self,
            text=_('Process'),
        )
        self.ButtonProcess.pack(side='left', padx=4, pady=4)
        self.configure(text=_('Process'))


if __name__ == '__main__':
    root = tk.Tk()
    root.title('File List')
    frame_title = FrameTitle(root)
    frame_title.pack(expand=True, fill='both', padx=4, pady=5)
    output_file = OutputFile(root)
    output_file.pack(expand=True, fill='both', padx=4, pady=5)
    output_folder = OutputFolder(root)
    output_folder.pack(expand=True, fill='both', padx=4, pady=5)
    process = Process(root)
    process.pack(expand=True, fill='both', padx=4, pady=5)

    root.mainloop()