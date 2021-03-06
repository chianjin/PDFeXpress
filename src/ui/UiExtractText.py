import tkinter as tk
import tkinter.ttk as ttk


class UiExtractText(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiExtractText, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='FrameLabelFont', text=_('Extract Text'))
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='20', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FramePDFFile = ttk.Labelframe(self)
        self.EntryPDFFile = ttk.Entry(self.FramePDFFile)
        self.pdf_file = tk.StringVar(value='')
        self.EntryPDFFile.configure(state='readonly', textvariable=self.pdf_file)
        self.EntryPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonPDFFile = ttk.Button(self.FramePDFFile)
        self.ButtonPDFFile.configure(text=_('Browser'))
        self.ButtonPDFFile.pack(ipadx='2', padx='4', pady='4', side='right')
        self.ButtonPDFFile.configure(command=self.get_pdf_file)
        self.FramePDFFile.configure(height='200', text=_('PDF File'), width='200')
        self.FramePDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameTextFile = ttk.Labelframe(self)
        self.EntryTextFile = ttk.Entry(self.FrameTextFile)
        self.text_file = tk.StringVar(value='')
        self.EntryTextFile.configure(state='readonly', textvariable=self.text_file)
        self.EntryTextFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonTextFile = ttk.Button(self.FrameTextFile)
        self.ButtonTextFile.configure(text=_('Browser'))
        self.ButtonTextFile.pack(ipadx='2', padx='4', pady='4', side='right')
        self.ButtonTextFile.configure(command=self.set_text_file)
        self.FrameTextFile.configure(height='200', text=_('Text File'), width='200')
        self.FrameTextFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.LabelProcessInfo.pack(padx='5', pady='5', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text=_('Extract'))
        self.ButtonProcess.pack(ipadx='2', padx='4', pady='4', side='right')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text=_('Extract Text'), width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_text_file(self):
        pass

    def process(self):
        pass
