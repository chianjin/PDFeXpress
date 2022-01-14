import tkinter as tk
import tkinter.ttk as ttk


class UiPDF2Images(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiPDF2Images, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='{Microsoft YaHei UI} 16 {bold}', text=_('PDF to Images'))
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
        self.FrameImagesDir = ttk.Labelframe(self)
        self.EntryImagesDir = ttk.Entry(self.FrameImagesDir)
        self.images_dir = tk.StringVar(value='')
        self.EntryImagesDir.configure(state='readonly', textvariable=self.images_dir)
        self.EntryImagesDir.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonImagesDir = ttk.Button(self.FrameImagesDir)
        self.ButtonImagesDir.configure(text=_('Browser'))
        self.ButtonImagesDir.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonImagesDir.configure(command=self.set_images_dir)
        self.FrameImagesDir.configure(height='200', text=_('Images Folder'), width='200')
        self.FrameImagesDir.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameOption = ttk.Labelframe(self)
        self.LabelImageFormat = ttk.Label(self.FrameOption)
        self.LabelImageFormat.configure(text=_('Image Format'))
        self.LabelImageFormat.pack(padx='4', pady='4', side='left')
        self.RadioButtonPNG = ttk.Radiobutton(self.FrameOption)
        self.image_format = tk.StringVar(value='png')
        self.RadioButtonPNG.configure(text='PNG', value='png', variable=self.image_format)
        self.RadioButtonPNG.pack(padx='4', pady='4', side='left')
        self.RadioButtonPNG.configure(command=self.set_image_format)
        self.CheckbuttonPNGAlpha = ttk.Checkbutton(self.FrameOption)
        self.image_alpha = tk.IntVar(value='')
        self.CheckbuttonPNGAlpha.configure(
                offvalue='0', onvalue='1', text=_('Transparent'), variable=self.image_alpha
                )
        self.CheckbuttonPNGAlpha.pack(padx='4', pady='4', side='left')
        self.CheckbuttonPNGAlpha.configure(command=self.set_image_alpha)
        self.RadioButtonJPEG = ttk.Radiobutton(self.FrameOption)
        self.RadioButtonJPEG.configure(text='JPEG', value='jpg', variable=self.image_format)
        self.RadioButtonJPEG.pack(padx='4', pady='4', side='left')
        self.RadioButtonJPEG.configure(command=self.set_image_format)
        self.LabelImageQuality = ttk.Label(self.FrameOption)
        self.LabelImageQuality.configure(state='disabled', text=_('Image Quality'))
        self.LabelImageQuality.pack(padx='4', pady='4', side='left')
        self.EntryImageQuality = ttk.Entry(self.FrameOption)
        self.image_quality = tk.IntVar(value='')
        self.EntryImageQuality.configure(
                justify='center', state='disabled', textvariable=self.image_quality, validate='focusout'
                )
        self.EntryImageQuality.configure(width='3')
        self.EntryImageQuality.pack(padx='4', pady='4', side='left')
        self.EntryImageQuality.configure(validatecommand=self.valid_image_quality)
        self.ScaleImageQuality = ttk.Scale(self.FrameOption)
        self.ScaleImageQuality.configure(from_='0', orient='horizontal', state='disabled', to='100')
        self.ScaleImageQuality.configure(value='80', variable=self.image_quality)
        self.ScaleImageQuality.pack(padx='4', pady='4', side='left')
        self.ScaleImageQuality.configure(command=self.set_image_quality)
        self.LabelImageDPI = ttk.Label(self.FrameOption)
        self.LabelImageDPI.configure(state='disabled', text='DPI')
        self.LabelImageDPI.pack(padx='4', pady='4', side='left')
        self.ComboboxImageDPI = ttk.Combobox(self.FrameOption)
        self.image_dpi = tk.IntVar(value='')
        self.ComboboxImageDPI.configure(
                justify='center', state='disabled', textvariable=self.image_dpi, validate='focusout'
                )
        self.ComboboxImageDPI.configure(values='96 144 192 240 288 336 384 432 480 528 576 624', width='4')
        self.ComboboxImageDPI.pack(padx='4', pady='4', side='left')
        self.ComboboxImageDPI.configure(validatecommand=self.valid_image_dpi)
        self.FrameOption.configure(height='200', text=_('Option'), width='200')
        self.FrameOption.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(justify='left', textvariable=self.app_info)
        self.LabelAppInfo.pack(fill='y', padx='4', pady='4', side='left')
        self.FrameSpacer = ttk.Frame(self.FrameProcess)
        self.FrameSpacer.configure(height='1', width='1')
        self.FrameSpacer.pack(expand='true', fill='y', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text=_('Convert'))
        self.ButtonProcess.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text=_('PDF to Images'), width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_images_dir(self):
        pass

    def set_image_format(self):
        pass

    def set_image_alpha(self):
        pass

    def valid_image_quality(self):
        pass

    def set_image_quality(self, scale_value):
        pass

    def valid_image_dpi(self):
        pass

    def process(self):
        pass
