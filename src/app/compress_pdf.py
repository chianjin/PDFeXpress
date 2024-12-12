import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename

from constant import FILE_WILDCARD
from widget import Process, FrameTitle, InputFile, OutputFile


class CompressPDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('Compress PDF'))
        self.FrameTitle.pack(fill='x', padx=4, pady=4)

        self.InputFile = InputFile(master=self)
        self.InputFile.pack(fill='x', padx=4, pady=4)

        self.Options = Options(master=self)
        self.Options.pack(fill='x', padx=4, pady=4)

        self.OutputFile = OutputFile(master=self)
        self.OutputFile.configure(text=_('PDF Output File'))
        self.OutputFile.pack(fill='x', padx=4, pady=4)
        self.OutputFile.ButtonOutputFile.configure(command=self.set_output_file)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Compress PDF'))
        self.Process.ButtonProcess.configure(text=_('Compress'), command=self.compress_pdf)
        self.Process.pack(fill='x', padx=4, pady=4)

    def set_output_file(self):
        initial_file = None
        initial_dir = None
        current_file = self.OutputFile.output_file.get()
        if current_file:
            initial_file = Path(current_file).name
            initial_dir = Path(current_file).parent
        else:
            current_file = self.InputFile.input_file.get()
            if current_file:
                initial_file = f'{Path(current_file).stem}-compressed.pdf'
                initial_dir = Path(current_file).parent

        file = asksaveasfilename(
            title=_('Select PDF Output File'),
            filetypes=FILE_WILDCARD['pdf'],
            defaultextension='.pdf',
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if file:
            self.OutputFile.output_file.set(Path(file))

    def compress_pdf(self):
        pass


class Options(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.LabelImageQuality = ttk.Label(master=self, text=_('Image Quality'))
        self.LabelImageQuality.pack(side='left', padx=4, pady=4)
        self.image_quality = tk.IntVar(value=85)
        self.EntryImageQuality = ttk.Entry(master=self, width=4, justify='center', textvariable=self.image_quality)
        self.EntryImageQuality.pack(side='left', padx=4, pady=4)

        ttk.Separator(master=self, orient='vertical').pack(side='left',fill='y', padx=14, pady=4)

        self.LabelMaxResolution = ttk.Label(master=self, text=_('Max Resolution'))
        self.LabelMaxResolution.pack(side='left', padx=4, pady=4)
        self.max_resolution = tk.IntVar(value=150)
        self.EntryMaxResolution = ttk.Entry(master=self, width=4, justify='center', textvariable=self.max_resolution)
        self.EntryMaxResolution.pack(side='left', padx=4, pady=4)
        self.LabelMaxResolutionUnit = ttk.Label(master=self, text='dpi')
        self.LabelMaxResolutionUnit.pack(side='left', padx=0, pady=4)


        self.configure(text=_('Options'))
        self.pack(fill='x', padx=4, pady=4)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Split PDF')
    split_pdf = CompressPDF(root)
    split_pdf.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
