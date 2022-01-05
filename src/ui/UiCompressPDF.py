import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiCompressPDF.ui"


class UiCompressPDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiCompressPDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.frame_name = tk.StringVar(value='压缩 PDF')
        self.LabelFrameName.configure(
                font='{Microsoft YaHei UI} 16 {bold}', text='压缩 PDF', textvariable=self.frame_name
                )
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
        self.FrameCompressedPDFFile = ttk.Labelframe(self)
        self.EntryCompressedPDFFile = ttk.Entry(self.FrameCompressedPDFFile)
        self.compressed_pdf_file = tk.StringVar(value='')
        self.EntryCompressedPDFFile.configure(state='readonly', textvariable=self.compressed_pdf_file)
        self.EntryCompressedPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonCompressedPDFFile = ttk.Button(self.FrameCompressedPDFFile)
        self.ButtonCompressedPDFFile.configure(text='浏览')
        self.ButtonCompressedPDFFile.pack(padx='4', pady='4', side='left')
        self.ButtonCompressedPDFFile.configure(command=self.set_compressed_pdf_file)
        self.FrameCompressedPDFFile.configure(height='200', text='输出文件', width='200')
        self.FrameCompressedPDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameOptions = ttk.Labelframe(self)
        self.LabelImageQuality = ttk.Label(self.FrameOptions)
        self.LabelImageQuality.configure(text='图像质量：')
        self.LabelImageQuality.pack(padx='4', pady='4', side='left')
        self.EntryImageQuality = ttk.Entry(self.FrameOptions)
        self.image_quality = tk.IntVar(value='')
        self.EntryImageQuality.configure(justify='center', textvariable=self.image_quality, width='3')
        self.EntryImageQuality.pack(pady='4', side='left')
        self.ScaleImageQuality = ttk.Scale(self.FrameOptions)
        self.ScaleImageQuality.configure(from_='0', orient='horizontal', to='100', value='80')
        self.ScaleImageQuality.configure(variable=self.image_quality)
        self.ScaleImageQuality.pack(padx='4', pady='4', side='left')
        self.ScaleImageQuality.configure(command=self.set_image_quality)
        self.FrameSpacer = ttk.Frame(self.FrameOptions)
        self.FrameSpacer.configure(height='1', width='20')
        self.FrameSpacer.pack(padx='4', pady='4', side='left')
        self.Label = ttk.Label(self.FrameOptions)
        self.max_dpi = tk.StringVar(value='最大分辨率：')
        self.Label.configure(font='TkDefaultFont', text='最大分辨率：', textvariable=self.max_dpi)
        self.Label.pack(pady='4', side='left')
        self.ComboboxDPI = ttk.Combobox(self.FrameOptions)
        self.image_dpi = tk.IntVar(value='')
        self.ComboboxDPI.configure(
                justify='center', state='readonly', textvariable=self.image_dpi, values='96 144 192 244 288 384 480 576'
                )
        self.ComboboxDPI.configure(width='3')
        self.ComboboxDPI.pack(pady='4', side='left')
        self.LabelDPIUnit = ttk.Label(self.FrameOptions)
        self.LabelDPIUnit.configure(text='dpi')
        self.LabelDPIUnit.pack(padx='4', pady='4', side='left')
        self.FrameOptions.configure(height='200', text='选项', width='200')
        self.FrameOptions.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelPDFInfo = ttk.Label(self.FrameProcess)
        self.pdf_info = tk.StringVar(value='')
        self.LabelPDFInfo.configure(textvariable=self.pdf_info)
        self.LabelPDFInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.process_info = tk.StringVar(value='')
        self.LabelProcessInfo.configure(textvariable=self.process_info)
        self.LabelProcessInfo.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text='压缩')
        self.ButtonProcess.pack(padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text='压缩 PDF', width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def help(self):
        pass

    def get_pdf_file(self):
        pass

    def set_compressed_pdf_file(self):
        pass

    def set_image_quality(self, scale_value):
        pass

    def process(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiCompressPDF(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
