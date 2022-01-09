import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiExtractImages.ui"


class UiExtractImages(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiExtractImages, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='{Microsoft YaHei UI} 16 {bold}', text='Extract Images')
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='10', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FramePDFFile = ttk.Labelframe(self)
        self.EntryPDFFile = ttk.Entry(self.FramePDFFile)
        self.pdf_file = tk.StringVar(value='')
        self.EntryPDFFile.configure(state='readonly', textvariable=self.pdf_file)
        self.EntryPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonPDFFile = ttk.Button(self.FramePDFFile)
        self.ButtonPDFFile.configure(text='Browser')
        self.ButtonPDFFile.pack(padx='4', pady='4', side='right')
        self.ButtonPDFFile.configure(command=self.get_pdf_file)
        self.FramePDFFile.configure(height='200', text='PDF File', width='200')
        self.FramePDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameImagesDir = ttk.Labelframe(self)
        self.EntryImagesDir = ttk.Entry(self.FrameImagesDir)
        self.images_dir = tk.StringVar(value='')
        self.EntryImagesDir.configure(state='readonly', textvariable=self.images_dir)
        self.EntryImagesDir.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonImagesDir = ttk.Button(self.FrameImagesDir)
        self.ButtonImagesDir.configure(text='Browser')
        self.ButtonImagesDir.pack(padx='4', pady='4', side='left')
        self.ButtonImagesDir.configure(command=self.set_images_dir)
        self.FrameImagesDir.configure(height='200', text='Images Folder', width='200')
        self.FrameImagesDir.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.LabelProcessInfo.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text='Extract')
        self.ButtonProcess.pack(padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text='Extract Images', width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_images_dir(self):
        pass

    def process(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiExtractImages(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
