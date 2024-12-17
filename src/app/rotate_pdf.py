import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo

import fitz
import tkinterdnd2

from utility import get_treeview_file_list, add_files_to_treeview, split_drop_data
from widget import FileList, Process, FrameTitle, OutputFolder


class RotatePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('Rotate PDF'))

        self.FileList = FileList(master=self)

        self.Options = Options(master=self)

        self.OutputFolder = OutputFolder(master=self)
        self.OutputFolder.configure(text=_('PDF Output Folder'))
        self.OutputFolder.ButtonOutputFolder.configure(command=self.set_output_folder)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Rotate PDF'))
        self.Process.ButtonProcess.configure(text=_('Rotate'), command=self.rotate_pdf)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        file_list = split_drop_data(event.data)
        file_list = [file for file in file_list if file.suffix.lower() == '.pdf']
        add_files_to_treeview(self.FileList.TreeviewFilelist, file_list)

    def set_output_folder(self):
        initial_dir = None
        current_folder = self.OutputFolder.output_folder.get()
        if current_folder:
            initial_dir = Path(current_folder)
        else:
            item_list = self.FileList.TreeviewFilelist.get_children()
            if item_list:
                current_file = self.FileList.TreeviewFilelist.entry(item_list[0])['text']
                initial_dir = Path(current_file).parent
        folder = askdirectory(
            title=_('Select PDF Output Folder'),
            initialdir=initial_dir
        )
        if folder:
            self.OutputFolder.output_folder.set(Path(folder))

    def rotate_pdf(self):
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
            angle = self.Options.rotation_angle.get()
            output_file = Path(output_folder) / f'{Path(input_file).stem}-rotated{angle}.pdf'
            with fitz.Document(input_file) as input_pdf:
                for page in input_pdf:
                    page.set_rotation(angle)
                input_pdf.save(output_file, garbage=4, deflate=True)
            self.Process.process.set(i)
            self.Process.ProgressBar.update_idletasks()
        self.Process.ProgressBar.grab_release()
        showinfo(title=_('Done'), message=_('Rotate Completed.'))
        self.Process.process.set(0)


class Options(ttk.LabelFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.AngleLabel = ttk.Label(master=self, text=_('Rotation Angle (Clockwise)'))
        self.AngleLabel.pack(side='left', padx=4, pady=4)
        self.rotation_angle = tk.IntVar(value=90)
        self.RadioButton90 = ttk.Radiobutton(master=self, text='90°', variable=self.rotation_angle, value=90)
        self.RadioButton90.pack(side='left', padx=4, pady=4)
        self.RadioButton180 = ttk.Radiobutton(master=self, text='180°', variable=self.rotation_angle, value=180)
        self.RadioButton180.pack(side='left', padx=4, pady=4)
        self.RadioButton270 = ttk.Radiobutton(master=self, text='270°', variable=self.rotation_angle, value=270)
        self.RadioButton270.pack(side='left', padx=4, pady=4)
        self.configure(text=_('Options'))
        self.pack(fill='x', padx=4, pady=4)


if __name__ == '__main__':
    root = tkinterdnd2.Tk()
    root.title('Rotate PDF')
    rotate_pdf = RotatePDF(root)
    rotate_pdf.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
