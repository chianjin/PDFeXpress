import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import ttk, Image
from tkinter.filedialog import askdirectory, asksaveasfilename

import fitz
import tkinterdnd2
from PIL import Image
from PIL.JpegImagePlugin import jpeg_factory

from constant import FILE_WILDCARD
from utility import get_treeview_file_list, drop_pdf_files_to_treeview, drop_pdf_file_to_entry
from widget import Process, FrameTitle, OutputFile, InputFile


class PDFToLongImage(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.default_options = {
            'image_resolution': 144,
            'jpeg_quality': 85,
        }

        self.FrameTitle = FrameTitle(master=self, frame_title=_('PDF to Long Image'))
        self.FrameTitle.pack(fill='x', padx=4, pady=4)

        self.InputFile = InputFile(master=self)
        self.InputFile.pack(fill='x', padx=4, pady=4)
        self.InputFile.input_file.trace('w', self.trace_input_file)

        self.Options = Options(master=self)
        self.Options.pack(fill='x', padx=4, pady=4)
        self.Options.jpeg_quality.set(self.default_options['jpeg_quality'])
        self.Options.image_resolution.set(self.default_options['image_resolution'])

        self.OutputFile = OutputFile(master=self)
        self.OutputFile.configure(text=_('Long Image File'))
        self.OutputFile.pack(fill='x', padx=4, pady=4)
        self.OutputFile.ButtonOutputFile.configure(command=self.set_output_file)

        self.Process = Process(master=self)
        self.Process.configure(text=_('PDF to Long Image'))
        self.Process.ButtonProcess.configure(text=_('Convert'), command=self.pdf_to_long_image)
        self.Process.pack(fill='x', padx=4, pady=4)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        drop_pdf_file_to_entry(self.InputFile.input_file, event)

    def trace_input_file(self, *args):
        input_file = self.InputFile.input_file.get()
        if input_file:
            self.OutputFile.output_file.set(Path(input_file).with_suffix('.jpg'))

    def set_output_file(self):
        initial_dir = None
        initial_file = None
        current_file = self.OutputFile.output_file.get()
        if current_file:
            initial_file = Path(current_file)
        else:
            initial_file = Path(self.InputFile.input_file.get()).with_suffix('.jpg')
        initial_dir = Path(initial_file).parent
        initial_file = Path(initial_file).name

        file = asksaveasfilename(
            title=_('Select PDF Output File'),
            filetypes=FILE_WILDCARD['jpg'],
            defaultextension='.jpg',
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if file:
            self.OutputFile.output_file.set(Path(file))

    def pdf_to_long_image(self):
        input_file = self.InputFile.input_file.get()
        output_file = self.OutputFile.output_file.get()
        if not input_file or not output_file:
            return None

        if self.Options.EntryImageResolution.get() == "":
            self.Options.image_resolution.set(self.default_options['image_resolution'])
        if self.Options.EntryJpegQuality.get() == "":
            self.Options.jpeg_quality.set(self.default_options['jpeg_quality'])

        image_resolution = self.Options.image_resolution.get()
        jpeg_quality = self.Options.jpeg_quality.get()

        zoom = image_resolution / 72
        matrix = fitz.Matrix(zoom, zoom)

        self.Process.ProgressBar.grab_set()
        self.Process.process.set(0)
        images = []
        with fitz.Document(input_file) as input_pdf:
            self.Process.ProgressBar.configure(maximum=input_pdf.page_count)
            for page_no, page in enumerate(input_pdf, start=1):
                pixmap = page.get_pixmap(matrix=matrix)
                image = Image.open(BytesIO(pixmap.tobytes()))
                images.append(image)
        self.Process.process.set(page_no)
        self.Process.ProgressBar.update_idletasks()

        output_height = sum(image.height for image in images)
        output_width = max(image.width for image in images)
        long_image = Image.new('RGB', (output_width, output_height))
        y = 0
        for image in images:
            long_image.paste(image, (0, y))
            y += image.height
        long_image.save(output_file, quality=jpeg_quality, dpi=(image_resolution, image_resolution))

        self.Process.ProgressBar.grab_release()


class Options(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.LabelImageResolution = ttk.Label(master=self, text=_('Resolution'))
        self.LabelImageResolution.pack(side='left', padx=4, pady=4)
        self.image_resolution = tk.IntVar(value=200)
        self.EntryImageResolution = ttk.Entry(
            master=self,
            width=4,
            justify='center',
            textvariable=self.image_resolution,
            validate='key',
            validatecommand=(self.register(self.validate_resolution), '%P')
        )
        self.EntryImageResolution.pack(side='left', padx=4, pady=4)
        self.LabelImageResolutionUnit = ttk.Label(master=self, text='dpi')
        self.LabelImageResolutionUnit.pack(side='left', padx=0, pady=4)
        ttk.Separator(master=self, orient='vertical').pack(side='left', fill='y', padx=14, pady=4)

        self.LabelJpegQuality = ttk.Label(master=self, text=_('Image Quality'))
        self.LabelJpegQuality.pack(side='left', padx=4, pady=4)
        self.jpeg_quality = tk.IntVar(value=85)
        self.EntryJpegQuality = ttk.Entry(
            master=self,
            width=4,
            justify='center',
            textvariable=self.jpeg_quality,
            validate='key',
            validatecommand=(self.register(self.validate_quality), '%P')
        )
        self.EntryJpegQuality.pack(side='left', padx=4, pady=4)

        self.configure(text=_('Options'))
        self.pack(fill='x', padx=4, pady=4)

    def validate_resolution(self, P):
        if P == "":
            return True
        try:
            value = int(P)
            return value > 0
        except ValueError:
            return False

    def validate_quality(self, P):
        if P == "":
            return True
        try:
            value = int(P)
            return value <= 100
        except ValueError:
            return False


if __name__ == '__main__':
    root = tkinterdnd2.Tk()
    root.title('PDF to Long Image')
    pdf_to_image = PDFToLongImage(root)
    pdf_to_image.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
