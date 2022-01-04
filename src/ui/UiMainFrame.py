import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiMainFrame.ui"


class UiMainFrame(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiMainFrame, self).__init__(master, **kw)
        self.LabelframeOperate = ttk.Labelframe(self)
        self.ButtonMergePDF = ttk.Button(self.LabelframeOperate)
        self.ButtonMergePDF.configure(style='Toolbutton', text='合并 PDF', width='10')
        self.ButtonMergePDF.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonMergePDF': self.set_operate(wid)
        self.ButtonMergePDF.configure(command=_wcmd)
        self.ButtonSplitPDF = ttk.Button(self.LabelframeOperate)
        self.ButtonSplitPDF.configure(style='Toolbutton', text='分割 PDF', width='10')
        self.ButtonSplitPDF.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonSplitPDF': self.set_operate(wid)
        self.ButtonSplitPDF.configure(command=_wcmd)
        self.ButtonRotatePDF = ttk.Button(self.LabelframeOperate)
        self.ButtonRotatePDF.configure(style='Toolbutton', text='旋转 PDF', width='10')
        self.ButtonRotatePDF.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonRotatePDF': self.set_operate(wid)
        self.ButtonRotatePDF.configure(command=_wcmd)
        self.ButtonCompressPDF = ttk.Button(self.LabelframeOperate)
        self.ButtonCompressPDF.configure(style='Toolbutton', text='压缩 PDF', width='10')
        self.ButtonCompressPDF.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonCompressPDF': self.set_operate(wid)
        self.ButtonCompressPDF.configure(command=_wcmd)
        self.ButtonExtractImages = ttk.Button(self.LabelframeOperate)
        self.ButtonExtractImages.configure(style='Toolbutton', text='提取图像', width='10')
        self.ButtonExtractImages.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonExtractImages': self.set_operate(wid)
        self.ButtonExtractImages.configure(command=_wcmd)
        self.ButtonExtractText = ttk.Button(self.LabelframeOperate)
        self.ButtonExtractText.configure(style='Toolbutton', text='提取文本', width='10')
        self.ButtonExtractText.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonExtractText': self.set_operate(wid)
        self.ButtonExtractText.configure(command=_wcmd)
        self.ButtonPDF2Images = ttk.Button(self.LabelframeOperate)
        self.ButtonPDF2Images.configure(style='Toolbutton', text='PDF 转图像', width='10')
        self.ButtonPDF2Images.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonPDF2Images': self.set_operate(wid)
        self.ButtonPDF2Images.configure(command=_wcmd)
        self.ButtonImages2PDF = ttk.Button(self.LabelframeOperate)
        self.ButtonImages2PDF.configure(style='Toolbutton', text='图像转 PDF', width='10')
        self.ButtonImages2PDF.pack(padx='4', pady='4', side='top')
        _wcmd = lambda wid='ButtonImages2PDF': self.set_operate(wid)
        self.ButtonImages2PDF.configure(command=_wcmd)
        self.LabelframeOperate.configure(height='200', text='操作', width='200')
        self.LabelframeOperate.pack(fill='y', padx='4', pady='4', side='left')
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
