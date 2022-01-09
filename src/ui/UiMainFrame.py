import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiMainFrame.ui"


class UiMainFrame(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiMainFrame, self).__init__(master, **kw)
        self.FrameOperateButtons = ttk.Labelframe(self)
        self.ButtonMergePDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonMergePDF.configure(text='合并 PDF')
        self.ButtonMergePDF.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonMergePDF': self.set_operate(wid)
        self.ButtonMergePDF.configure(command=_wcmd)
        self.ButtonSplitPDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonSplitPDF.configure(text='分割 PDF')
        self.ButtonSplitPDF.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonSplitPDF': self.set_operate(wid)
        self.ButtonSplitPDF.configure(command=_wcmd)
        self.ButtonRotatePDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonRotatePDF.configure(text='旋转 PDF')
        self.ButtonRotatePDF.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonRotatePDF': self.set_operate(wid)
        self.ButtonRotatePDF.configure(command=_wcmd)
        self.ButtonCompressPDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonCompressPDF.configure(text='压缩 PDF')
        self.ButtonCompressPDF.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonCompressPDF': self.set_operate(wid)
        self.ButtonCompressPDF.configure(command=_wcmd)
        self.ButtonExtractImages = ttk.Button(self.FrameOperateButtons)
        self.ButtonExtractImages.configure(text='提取图像')
        self.ButtonExtractImages.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonExtractImages': self.set_operate(wid)
        self.ButtonExtractImages.configure(command=_wcmd)
        self.ButtonExtractText = ttk.Button(self.FrameOperateButtons)
        self.ButtonExtractText.configure(text='提取文本')
        self.ButtonExtractText.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonExtractText': self.set_operate(wid)
        self.ButtonExtractText.configure(command=_wcmd)
        self.ButtonPDF2Images = ttk.Button(self.FrameOperateButtons)
        self.ButtonPDF2Images.configure(text='PDF 转图像')
        self.ButtonPDF2Images.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonPDF2Images': self.set_operate(wid)
        self.ButtonPDF2Images.configure(command=_wcmd)
        self.ButtonImages2PDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonImages2PDF.configure(text='图像转 PDF')
        self.ButtonImages2PDF.pack(fill='x', padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonImages2PDF': self.set_operate(wid)
        self.ButtonImages2PDF.configure(command=_wcmd)
        self.FrameOperateButtons.configure(height='200', text='操作', width='200')
        self.FrameOperateButtons.pack(fill='y', padx='4', pady='4', side='left')
        self.FrameOperate = ttk.Frame(self)
        self.FrameOperate.configure(height='200', width='200')
        self.FrameOperate.pack(expand='true', fill='both', side='left')

    def set_operate(self, widget_id):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiMainFrame(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
