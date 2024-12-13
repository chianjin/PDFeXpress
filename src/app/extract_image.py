import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory

import fitz
import tkinterdnd2

from utility import get_treeview_file_list, drop_pdf_files_to_treeview
from widget import FileList, Process, FrameTitle, OutputFolder


class ExtractImage(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('Extract Image'))
        self.FrameTitle.pack(fill='x', padx=4, pady=4)

        self.FileList = FileList(master=self)
        self.FileList.pack(expand=True, fill='both', padx=4, pady=4)
        self.FileList.configure(text=_('PDF File List'))

        self.OutputFolder = OutputFolder(master=self)
        self.OutputFolder.configure(text=_('Image Output Folder'))
        self.OutputFolder.pack(fill='x', padx=4, pady=4)
        self.OutputFolder.ButtonOutputFolder.configure(command=self.set_output_folder)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Extract Image'))
        self.Process.ButtonProcess.configure(text=_('Extract'), command=self.extract_image)
        self.Process.pack(fill='x', padx=4, pady=4)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        drop_pdf_files_to_treeview(self.FileList.TreeviewFilelist, event)

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
            title=_('Select Image Output Folder'),
            initialdir=initial_dir
        )
        if folder:
            self.OutputFolder.output_folder.set(Path(folder))

    def extract_image(self):
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
            with fitz.Document(input_file) as input_pdf:
                page_no_width = len(str(input_pdf.page_count))
                for page_no, page in enumerate(input_pdf, start=1):
                    images = page.get_images()
                    for image_no, image_info in enumerate(images, start=1):
                        print(image_no)
                        xref = image_info[0]
                        image_data = input_pdf.extract_image(xref)
                        ext = image_data['ext']
                        image = image_data['image']
                        output_file = f'{Path(input_file).stem}-P{page_no:0{page_no_width}d}-{image_no:02d}.{ext}'
                        print(output_file)
                        output_file = Path(output_folder) / output_file
                        with open(output_file, 'wb') as f:
                            f.write(image)
            self.Process.process.set(i)
            self.Process.ProgressBar.update_idletasks()
        self.Process.ProgressBar.grab_release()


if __name__ == '__main__':
    root = tkinterdnd2.Tk()
    root.title('Extract Text')
    extract_image = ExtractImage(root)
    extract_image.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
