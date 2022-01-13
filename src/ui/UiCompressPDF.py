import tkinter as tk
import tkinter.ttk as ttk

from constants import TRANSLATER as _


class UiCompressPDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiCompressPDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='{Microsoft YaHei UI} 16 {bold}', text=_('Compress PDF'))
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='10', width='200')
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
        self.FrameCompressedPDFFile = ttk.Labelframe(self)
        self.EntryCompressedPDFFile = ttk.Entry(self.FrameCompressedPDFFile)
        self.compressed_pdf_file = tk.StringVar(value='')
        self.EntryCompressedPDFFile.configure(state='readonly', textvariable=self.compressed_pdf_file)
        self.EntryCompressedPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonCompressedPDFFile = ttk.Button(self.FrameCompressedPDFFile)
        self.ButtonCompressedPDFFile.configure(text=_('Browser'))
        self.ButtonCompressedPDFFile.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonCompressedPDFFile.configure(command=self.set_compressed_pdf_file)
        self.FrameCompressedPDFFile.configure(height='200', text=_('Compressed PDF File'), width='200')
        self.FrameCompressedPDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameOption = ttk.Labelframe(self)
        self.LabelImageQuality = ttk.Label(self.FrameOption)
        self.LabelImageQuality.configure(text=_('Image Quality'))
        self.LabelImageQuality.pack(padx='4', pady='4', side='left')
        self.EntryImageQuality = ttk.Entry(self.FrameOption)
        self.image_quality = tk.IntVar(value='')
        self.EntryImageQuality.configure(justify='center', textvariable=self.image_quality, width='3')
        self.EntryImageQuality.pack(padx='4', pady='4', side='left')
        self.ScaleImageQuality = ttk.Scale(self.FrameOption)
        self.ScaleImageQuality.configure(from_='0', orient='horizontal', to='100', value='80')
        self.ScaleImageQuality.configure(variable=self.image_quality)
        self.ScaleImageQuality.pack(padx='4', pady='4', side='left')
        self.ScaleImageQuality.configure(command=self.set_image_quality)
        self.FrameSpacer = ttk.Frame(self.FrameOption)
        self.FrameSpacer.configure(height='1', width='20')
        self.FrameSpacer.pack(padx='4', pady='4', side='left')
        self.LabelImageMaxDPI = ttk.Label(self.FrameOption)
        self.LabelImageMaxDPI.configure(text=_('Max DPI'))
        self.LabelImageMaxDPI.pack(padx='4', pady='4', side='left')
        self.ComboboxDPI = ttk.Combobox(self.FrameOption)
        self.image_max_dpi = tk.IntVar(value='')
        self.ComboboxDPI.configure(
                justify='center', state='readonly', textvariable=self.image_max_dpi,
                values='96 144 192 244 288 384 480 576'
                )
        self.ComboboxDPI.configure(width='3')
        self.ComboboxDPI.pack(padx='4', pady='4', side='left')
        self.FrameOption.configure(height='200', text=_('Option'), width='200')
        self.FrameOption.pack(fill='x', padx='4', pady='4', side='top')
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
        self.ButtonProcess.configure(state='disabled', text=_('Compress'))
        self.ButtonProcess.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text=_('Compress PDF'), width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_compressed_pdf_file(self):
        pass

    def set_image_quality(self, scale_value):
        pass

    def process(self):
        pass
