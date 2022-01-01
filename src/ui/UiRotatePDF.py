import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiRotatePDF.ui"


class UiRotatePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiRotatePDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.frame_name = tk.StringVar(value='旋转 PDF')
        self.LabelFrameName.configure(
                font='{Microsoft YaHei UI} 16 {bold}', text='旋转 PDF',
                textvariable=self.frame_name
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
        self.FrameRotatedPDFFile = ttk.Labelframe(self)
        self.EntryRotatedPDFFile = ttk.Entry(self.FrameRotatedPDFFile)
        self.rotated_pdf_file = tk.StringVar(value='')
        self.EntryRotatedPDFFile.configure(textvariable=self.rotated_pdf_file)
        self.EntryRotatedPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonRotatedPDFFile = ttk.Button(self.FrameRotatedPDFFile)
        self.ButtonRotatedPDFFile.configure(text='浏览')
        self.ButtonRotatedPDFFile.pack(padx='4', pady='4', side='left')
        self.ButtonRotatedPDFFile.configure(command=self.set_rotated_pdf_file)
        self.FrameRotatedPDFFile.configure(height='200', text='输出 PDF 文件', width='200')
        self.FrameRotatedPDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameOptions = ttk.Labelframe(self)
        self.LabelDegree = ttk.Label(self.FrameOptions)
        self.LabelDegree.configure(text='旋转角度')
        self.LabelDegree.pack(padx='4', pady='4', side='left')
        self.ComboboxDegree = ttk.Combobox(self.FrameOptions)
        self.rotate_degree = tk.StringVar(value='')
        self.ComboboxDegree.configure(
                state='readonly', textvariable=self.rotate_degree, values='90° 180° 270°',
                width='4'
                )
        self.ComboboxDegree.pack(padx='4', pady='4', side='left')
        self.FrameSpacer = ttk.Frame(self.FrameOptions)
        self.FrameSpacer.configure(height='1', width='20')
        self.FrameSpacer.pack(padx='4', pady='4', side='left')
        self.RadiobuttonCW = ttk.Radiobutton(self.FrameOptions)
        self.rotate_direction = tk.StringVar(value='cw')
        self.RadiobuttonCW.configure(text='顺时针', value='cw', variable=self.rotate_direction)
        self.RadiobuttonCW.pack(padx='4', pady='4', side='left')
        self.RadiobuttonCCW = ttk.Radiobutton(self.FrameOptions)
        self.RadiobuttonCCW.configure(text='逆时针', value='ccw', variable=self.rotate_direction)
        self.RadiobuttonCCW.pack(padx='4', pady='4', side='left')
        self.FrameSpacer2 = ttk.Frame(self.FrameOptions)
        self.FrameSpacer2.configure(height='1', width='20')
        self.FrameSpacer2.pack(padx='4', pady='4', side='left')
        self.Checkbutton1 = ttk.Checkbutton(self.FrameOptions)
        self.use_src_dir = tk.StringVar(value='')
        self.Checkbutton1.configure(offvalue='0', onvalue='1', text='输出到原目录', variable=self.use_src_dir)
        self.Checkbutton1.pack(padx='4', pady='4', side='left')
        self.Checkbutton1.configure(command=self.set_use_src_dir)
        self.FrameOptions.configure(height='200', text='选项', width='200')
        self.FrameOptions.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.Progressbar = ttk.Progressbar(self.FrameProcess)
        self.progress = tk.IntVar(value='')
        self.Progressbar.configure(orient='horizontal', variable=self.progress)
        self.Progressbar.pack(fill='x', padx='4', pady='4', side='top')
        self.LabelPDFInfo = ttk.Label(self.FrameProcess)
        self.pdf_info = tk.StringVar(value='')
        self.LabelPDFInfo.configure(textvariable=self.pdf_info)
        self.LabelPDFInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.process_info = tk.StringVar(value='')
        self.LabelProcessInfo.configure(textvariable=self.process_info)
        self.LabelProcessInfo.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text='旋转')
        self.ButtonProcess.pack(padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text='旋转 PDF', width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_rotated_pdf_file(self):
        pass

    def set_use_src_dir(self):
        pass

    def process(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiRotatePDF(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
