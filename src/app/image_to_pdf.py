from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askopenfilenames, askdirectory

import fitz
import tkinterdnd2

from constant import FILE_WILDCARD
from utility import get_treeview_file_list, drop_image_files_to_treeview
from widget import FileListOrdered, OutputFile, Process, FrameTitle


class ImageToPDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.Title = FrameTitle(master=self, frame_title=_('Image to PDF'))
        self.Title.pack(fill='x', padx=4, pady=4)

        self.FileList = FileListOrdered(master=self)
        self.FileList.pack(expand=True, fill='both', padx=4, pady=4)
        self.FileList.configure(text=_('Image File List'))
        self.FileList.ButtonAddFiles.configure(command=self.add_files)
        self.FileList.ButtonAddFolder.configure(command=self.add_folder)

        self.OutputFile = OutputFile(master=self)
        self.OutputFile.configure(text=_('Output PDF File'))
        self.OutputFile.pack(fill='x', padx=4, pady=4)
        self.OutputFile.ButtonOutputFile.configure(command=self.set_output_file)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Image to PDF'))
        self.Process.ButtonProcess.configure(text=_('Convert'), command=self.image_to_pdf)
        self.Process.pack(fill='x', padx=4, pady=4)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        drop_image_files_to_treeview(self.FileList.TreeviewFilelist, event)

    def add_files(self):
        files = askopenfilenames(
            title=_('Select Image Files'),
            filetypes=FILE_WILDCARD['image']
        )
        if files:
            self.FileList._add_files(files)

    def add_folder(self):
        folder = askdirectory(title=_('Select Folder'))
        file_list = []
        if folder:
            extensions = FILE_WILDCARD['image'][0][1]
            for ext in extensions.split(';'):
                files = Path(folder).glob(ext)
                if files:
                    file_list.extend(files)
            file_list.sort()
            self.FileList._add_files(file_list)

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
                initial_file = f'{Path(current_file).stem}.pdf'
        file = asksaveasfilename(
            title=_('Select PDF Output File'),
            filetypes=FILE_WILDCARD['pdf'],
            defaultextension='.pdf',
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if file:
            self.OutputFile.output_file.set(Path(file))

    def image_to_pdf(self):
        file_list = get_treeview_file_list(self.FileList.TreeviewFilelist)
        if not file_list:
            return None
        output_file = self.OutputFile.output_file.get()
        if not output_file:
            return None

        self.Process.ProgressBar.grab_set()
        self.Process.process.set(0)
        self.Process.ProgressBar.configure(maximum=len(file_list))
        with fitz.Document() as output_pdf:
            for i, input_file in enumerate(file_list, start=1):
                with fitz.Document(input_file) as image_file:
                    pdf_bytes = image_file.convert_to_pdf()
                    with fitz.Document('pdf', stream=pdf_bytes) as image_pdf:
                        output_pdf.insert_pdf(image_pdf)
                self.Process.process.set(i)
                self.Process.update_idletasks()
            output_pdf.save(output_file)
        self.Process.ProgressBar.grab_release()


if __name__ == '__main__':
    root = tkinterdnd2.Tk()
    root.title('Image t PDF')
    image_to_pdf = ImageToPDF(root)
    image_to_pdf.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
