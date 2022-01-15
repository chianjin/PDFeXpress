import tkinter.ttk as ttk


class UiMainFrame(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiMainFrame, self).__init__(master, **kw)
        self.FrameOperateButtons = ttk.Labelframe(self)
        self.ButtonMergePDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonMergePDF.configure(text=_('Merge PDF'))
        self.ButtonMergePDF.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='MergePDF'): self.set_operate(wid)

        self.ButtonMergePDF.configure(command=_w_cmd)
        self.ButtonSplitPDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonSplitPDF.configure(text=_('Split PDF'))
        self.ButtonSplitPDF.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='SplitPDF'): self.set_operate(wid)

        self.ButtonSplitPDF.configure(command=_w_cmd)
        self.ButtonRotatePDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonRotatePDF.configure(text=_('Rotate PDF'))
        self.ButtonRotatePDF.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='RotatePDF'): self.set_operate(wid)

        self.ButtonRotatePDF.configure(command=_w_cmd)
        self.ButtonCompressPDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonCompressPDF.configure(text=_('Compress PDF'))
        self.ButtonCompressPDF.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='CompressPDF'): self.set_operate(wid)

        self.ButtonCompressPDF.configure(command=_w_cmd)
        self.ButtonExtractImages = ttk.Button(self.FrameOperateButtons)
        self.ButtonExtractImages.configure(text=_('Extract Images'))
        self.ButtonExtractImages.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='ExtractImages'): self.set_operate(wid)

        self.ButtonExtractImages.configure(command=_w_cmd)
        self.ButtonExtractText = ttk.Button(self.FrameOperateButtons)
        self.ButtonExtractText.configure(text=_('Extract Text'))
        self.ButtonExtractText.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='ExtractText'): self.set_operate(wid)

        self.ButtonExtractText.configure(command=_w_cmd)
        self.ButtonPDF2Images = ttk.Button(self.FrameOperateButtons)
        self.ButtonPDF2Images.configure(text=_('PDF to Images'))
        self.ButtonPDF2Images.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='PDF2Images'): self.set_operate(wid)

        self.ButtonPDF2Images.configure(command=_w_cmd)
        self.ButtonImages2PDF = ttk.Button(self.FrameOperateButtons)
        self.ButtonImages2PDF.configure(text=_('Images to PDF'))
        self.ButtonImages2PDF.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')

        def _w_cmd(wid='Images2PDF'): self.set_operate(wid)

        self.ButtonImages2PDF.configure(command=_w_cmd)
        self.FrameOperateButtons.configure(height='200', text=_('Operate'), width='200')
        self.FrameOperateButtons.pack(fill='y', padx='4', pady='4', side='left')

    def set_operate(self, widget_id):
        pass
