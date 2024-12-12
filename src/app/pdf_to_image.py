import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import ttk, Image
from tkinter.filedialog import askdirectory

import fitz
from PIL import Image

from utility import get_treeview_file_list
from widget import Process, FrameTitle, OutputFolder, InputFile, FileList


class PDFToImage(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('PDF to Image'))
        self.FrameTitle.pack(fill='x', padx=4, pady=4)

        self.Filelist = FileList(master=self)
        self.Filelist.pack(expand=True, fill='x', padx=4, pady=4)
        self.Filelist.configure(text=_('PDF File List'))

        self.Options = Options(master=self)
        self.Options.pack(fill='x', padx=4, pady=4)

        self.OutputFolder = OutputFolder(master=self)
        self.OutputFolder.configure(text=_('Image Output Folder'))
        self.OutputFolder.pack(fill='x', padx=4, pady=4)
        self.OutputFolder.ButtonOutputFolder.configure(command=self.set_output_folder)

        self.Process = Process(master=self)
        self.Process.configure(text=_('PDF to Image'))
        self.Process.ButtonProcess.configure(text=_('Convert'), command=self.pdf_to_image)
        self.Process.pack(fill='x', padx=4, pady=4)

    def set_output_folder(self):
        initial_dir = None
        current_folder = self.OutputFolder.output_folder.get()
        if current_folder:
            initial_dir = Path(current_folder)
        else:
            file_list = get_treeview_file_list(self.Filelist.TreeviewFilelist)
            if file_list:
                current_file = file_list[0]
                initial_dir = Path(current_file).parent
        folder = askdirectory(
            title=_('Select PDF Output Folder'),
            initialdir=initial_dir
        )
        if folder:
            self.OutputFolder.output_folder.set(Path(folder))

    def pdf_to_image(self):
        file_list = get_treeview_file_list(self.Filelist.TreeviewFilelist)
        if not file_list:
            return None
        output_folder = self.OutputFolder.output_folder.get()
        if not output_folder:
            return None

        image_resolution= self.Options.image_resolution.get()
        image_format = self.Options.image_format.get()
        png_transparent = self.Options.png_transparent.get()
        jpeg_quality = self.Options.jpeg_quality.get()

        zoom = image_resolution / 96 * 4 / 3  # actually 72
        matrix = fitz.Matrix(zoom, zoom)

        self.Process.ProgressBar.grab_set()
        self.Process.process.set(0)
        self.Process.ProgressBar.configure(maximum=len(file_list))

        for i, input_file in enumerate(file_list, start=1):
            with fitz.Document(input_file) as input_pdf:
                page_no_width = len(str(input_pdf.page_count))
                for page_no, page in enumerate(input_pdf):
                    output_file = f'{Path(input_file).stem}-P{page_no:0{page_no_width}d}.{image_format}'
                    output_file = Path(output_folder) / output_file
                    if image_format == 'png':
                        pixmap = page.get_pixmap(matrix=matrix, alpha=png_transparent)
                        pixmap.save(output_file)
                    elif image_format == 'jpg':
                        pixmap = page.get_pixmap(matrix=matrix)
                        image = Image.open(BytesIO(pixmap.tobytes()))
                        image.save(output_file, quality=jpeg_quality, dpi=(image_resolution, image_resolution))
                        image.close()
            self.Process.process.set(i)
            self.Process.ProgressBar.update_idletasks()
        self.Process.ProgressBar.grab_release()


class Options(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.LabelImageResolution = ttk.Label(master=self, text=_('Resolution'))
        self.LabelImageResolution.pack(side='left', padx=4, pady=4)
        self.image_resolution = tk.IntVar(value=200)
        self.EntryImageResolution = ttk.Entry(master=self, width=4, justify='center', textvariable=self.image_resolution)
        self.EntryImageResolution.pack(side='left', padx=4, pady=4)
        self.LabelImageResolutionUnit = ttk.Label(master=self, text='dpi')
        self.LabelImageResolutionUnit.pack(side='left', padx=0, pady=4)
        ttk.Separator(master=self, orient='vertical').pack(side='left',fill='y', padx=14, pady=4)
        self.LabelImageFormat = ttk.Label(master=self, text=_('Image Format'))
        self.LabelImageFormat.pack(side='left', padx=4, pady=4)
        self.image_format = tk.StringVar(value='png')
        self.RadioButtonPNG = ttk.Radiobutton(
            master=self,
            text='PNG',
            variable=self.image_format,
            value='png'
        )
        self.RadioButtonPNG.pack(side='left', padx=4, pady=4)
        self.png_transparent = tk.BooleanVar(value=True)  # default is transparent
        self.CheckboxPngTransparent = tk.Checkbutton(
            master=self,
            text=_('Transparent'),
            variable=self.png_transparent,
            onvalue=True,
            offvalue=False
        )
        self.CheckboxPngTransparent.pack(side='left', padx=4, pady=4)
        self.RadioButtonJPG = ttk.Radiobutton(
            master=self,
            text='JPG',
            variable=self.image_format,
            value='jpg'
        )
        self.RadioButtonJPG.pack(side='left', padx=4, pady=4)
        self.LabelJpegQuality = ttk.Label(master=self, text=_('Image Quality'))
        self.LabelJpegQuality.pack(side='left', padx=4, pady=4)
        self.jpeg_quality = tk.IntVar(value=85)
        self.EntryJpegQuality = ttk.Entry(master=self, width=4, justify='center', textvariable=self.jpeg_quality)
        self.EntryJpegQuality.pack(side='left', padx=4, pady=4)

        self.configure(text=_('Options'))
        self.pack(fill='x', padx=4, pady=4)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('PDF to Image')
    pdf_to_image = PDFToImage(root)
    pdf_to_image.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
