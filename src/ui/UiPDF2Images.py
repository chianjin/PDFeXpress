import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiPDF2Images.ui"


class UiPDF2Images(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiPDF2Images, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.frame_name = tk.StringVar(value='PDF 转换为图像')
        self.LabelFrameName.configure(
            font='{Microsoft YaHei UI} 16 {bold}', text='PDF 转换为图像', textvariable=self.frame_name
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
        self.FrameImagesDir = ttk.Labelframe(self)
        self.EntryImagesDir = ttk.Entry(self.FrameImagesDir)
        self.images_dir = tk.StringVar(value='')
        self.EntryImagesDir.configure(state='readonly', textvariable=self.images_dir)
        self.EntryImagesDir.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonImagesDir = ttk.Button(self.FrameImagesDir)
        self.ButtonImagesDir.configure(text='浏览')
        self.ButtonImagesDir.pack(padx='4', pady='4', side='left')
        self.ButtonImagesDir.configure(command=self.set_images_dir)
        self.FrameImagesDir.configure(height='200', text='输出目录', width='200')
        self.FrameImagesDir.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameOptions = ttk.Labelframe(self)
        self.LabelImageDPI = ttk.Label(self.FrameOptions)
        self.LabelImageDPI.configure(text='分辨率')
        self.LabelImageDPI.pack(padx='4', pady='4', side='left')
        self.ComboboxImageDPI = ttk.Combobox(self.FrameOptions)
        self.image_dpi = tk.IntVar(value='')
        self.ComboboxImageDPI.configure(
            justify='center', textvariable=self.image_dpi, validate='focusout',
            values='96 144 192 240 288 336 384 432 480 528 576 624'
            )
        self.ComboboxImageDPI.configure(width='4')
        self.ComboboxImageDPI.pack(padx='4', pady='4', side='left')
        self.ComboboxImageDPI.configure(validatecommand=self.valid_image_dpi)
        self.LabelImageDPIUnit = ttk.Label(self.FrameOptions)
        self.LabelImageDPIUnit.configure(text='dpi')
        self.LabelImageDPIUnit.pack(padx='0', pady='4', side='left')
        self.Frame2 = ttk.Frame(self.FrameOptions)
        self.Frame2.configure(height='1', width='20')
        self.Frame2.pack(side='left')
        self.LabelImageQuality = ttk.Label(self.FrameOptions)
        self.LabelImageQuality.configure(text='图像质量')
        self.LabelImageQuality.pack(padx='4', pady='4', side='left')
        self.EntryImageQuality = ttk.Entry(self.FrameOptions)
        self.image_quality = tk.IntVar(value='')
        self.EntryImageQuality.configure(
            justify='center', textvariable=self.image_quality, validate='focusout', width='3'
            )
        self.EntryImageQuality.pack(pady='4', side='left')
        self.EntryImageQuality.configure(validatecommand=self.valid_image_quality)
        self.ScaleImageQuality = ttk.Scale(self.FrameOptions)
        self.ScaleImageQuality.configure(from_='0', orient='horizontal', to='100', value='75')
        self.ScaleImageQuality.configure(variable=self.image_quality)
        self.ScaleImageQuality.pack(padx='4', pady='4', side='left')
        self.ScaleImageQuality.configure(command=self.set_image_quality)
        self.FrameOptions.configure(height='200', text='选项', width='200')
        self.FrameOptions.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(justify='left', textvariable=self.app_info)
        self.LabelAppInfo.pack(fill='y', padx='4', pady='4', side='left')
        self.FrameSpacer = ttk.Frame(self.FrameProcess)
        self.FrameSpacer.configure(height='1', width='1')
        self.FrameSpacer.pack(expand='true', fill='y', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text='转换')
        self.ButtonProcess.pack(padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text='转换 PDF', width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_images_dir(self):
        pass

    def valid_image_dpi(self):
        pass

    def valid_image_quality(self):
        pass

    def set_image_quality(self, scale_value):
        pass

    def process(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiPDF2Images(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
