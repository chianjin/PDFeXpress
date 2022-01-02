import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiExtractText.ui"


class UiExtractText(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiExtractText, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.frame_name = tk.StringVar(value='提取文本')
        self.LabelFrameName.configure(font='{Microsoft YaHei UI} 16 {bold}', text='提取文本', textvariable=self.frame_name)
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='10', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FramePDFFile = ttk.Labelframe(self)
        self.EntryPDFFile = ttk.Entry(self.FramePDFFile)
        self.pdf_file = tk.StringVar(value='')
        self.EntryPDFFile.configure(state='readonly', textvariable=self.pdf_file)
        self.EntryPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonPDFFile = ttk.Button(self.FramePDFFile)
        self.ButtonPDFFile.configure(text='浏览')
        self.ButtonPDFFile.pack(padx='4', pady='4', side='right')
        self.ButtonPDFFile.configure(command=self.get_pdf_file)
        self.FramePDFFile.configure(height='200', text='PDF 文件', width='200')
        self.FramePDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameTextFile = ttk.Labelframe(self)
        self.EntryTextFile = ttk.Entry(self.FrameTextFile)
        self.text_file = tk.StringVar(value='')
        self.EntryTextFile.configure(state='disabled', textvariable=self.text_file)
        self.EntryTextFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonTextFile = ttk.Button(self.FrameTextFile)
        self.ButtonTextFile.configure(text='浏览')
        self.ButtonTextFile.pack(padx='4', pady='4', side='right')
        self.ButtonTextFile.configure(command=self.set_text_file)
        self.FrameTextFile.configure(height='200', text='输出文件', width='200')
        self.FrameTextFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.LabelProcessInfo.pack(padx='5', pady='5', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text='提取')
        self.ButtonProcess.pack(padx='4', pady='4', side='right')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text='提取文本', width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_text_file(self):
        pass

    def process(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiExtractText(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
