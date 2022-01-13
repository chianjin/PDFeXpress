import tkinter as tk
import tkinter.ttk as ttk

from constants import TRANSLATER as _


class UiSplitPDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiSplitPDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='{Microsoft YaHei UI} 16 {bold}', text=_('Split PDF'))
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
        self.FrameSplitPDFDir = ttk.Labelframe(self)
        self.EntrySplitPDFDir = ttk.Entry(self.FrameSplitPDFDir)
        self.split_pdf_dir = tk.StringVar(value='')
        self.EntrySplitPDFDir.configure(state='readonly', textvariable=self.split_pdf_dir)
        self.EntrySplitPDFDir.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonSplitPDFDir = ttk.Button(self.FrameSplitPDFDir)
        self.ButtonSplitPDFDir.configure(text=_('Browser'))
        self.ButtonSplitPDFDir.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonSplitPDFDir.configure(command=self.set_split_pdf_dir)
        self.FrameSplitPDFDir.configure(height='200', text=_('Split PDF Folder'), width='200')
        self.FrameSplitPDFDir.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameOption = ttk.Labelframe(self)
        self.FrameSplitMode = ttk.Frame(self.FrameOption)
        self.RadiobuttonSplitSingle = ttk.Radiobutton(self.FrameSplitMode)
        self.split_mode = tk.StringVar(value='single')
        self.RadiobuttonSplitSingle.configure(
                state='disabled', text=_('Per Page'), value='single', variable=self.split_mode
                )
        self.RadiobuttonSplitSingle.pack(padx='4', pady='4', side='left')
        self.RadiobuttonSplitSingle.configure(command=self.set_split_mode)
        self.RadiobuttonSplitPage = ttk.Radiobutton(self.FrameSplitMode)
        self.RadiobuttonSplitPage.configure(
                state='disabled', text=_('By Pages'), value='page', variable=self.split_mode
                )
        self.RadiobuttonSplitPage.pack(padx='4', pady='4', side='left')
        self.RadiobuttonSplitPage.configure(command=self.set_split_mode)
        self.EntrySplitPage = ttk.Entry(self.FrameSplitMode)
        self.split_page = tk.IntVar(value='')
        self.EntrySplitPage.configure(
                justify='center', state='disabled', textvariable=self.split_page, validate='focusout'
                )
        self.EntrySplitPage.configure(width='4')
        self.EntrySplitPage.pack(padx='4', pady='4', side='left')
        self.EntrySplitPage.configure(validatecommand=self.valid_page)
        self.RadiobuttonSplitCount = ttk.Radiobutton(self.FrameSplitMode)
        self.RadiobuttonSplitCount.configure(
                state='disabled', text=_('By Count'), value='count', variable=self.split_mode
                )
        self.RadiobuttonSplitCount.pack(padx='4', pady='4', side='left')
        self.RadiobuttonSplitCount.configure(command=self.set_split_mode)
        self.ComboboxSplitCount = ttk.Combobox(self.FrameSplitMode)
        self.split_count = tk.IntVar(value='')
        self.ComboboxSplitCount.configure(justify='center', state='disabled', textvariable=self.split_count, width='4')
        self.ComboboxSplitCount.pack(padx='4', pady='4', side='left')
        self.RadiobuttonSplitRange = ttk.Radiobutton(self.FrameSplitMode)
        self.RadiobuttonSplitRange.configure(
                state='disabled', text=_('By Range'), value='range', variable=self.split_mode
                )
        self.RadiobuttonSplitRange.pack(padx='4', pady='4', side='left')
        self.RadiobuttonSplitRange.configure(command=self.set_split_mode)
        self.EntrySplitRangeStart = ttk.Entry(self.FrameSplitMode)
        self.split_range_start = tk.IntVar(value='')
        self.EntrySplitRangeStart.configure(
                justify='center', state='disabled', textvariable=self.split_range_start, validate='focusout'
                )
        self.EntrySplitRangeStart.configure(width='5')
        self.EntrySplitRangeStart.pack(padx='4', pady='4', side='left')
        self.EntrySplitRangeStart.configure(validatecommand=self.valid_start)
        self.LabelSplitRangeTo = ttk.Label(self.FrameSplitMode)
        self.LabelSplitRangeTo.configure(state='disabled', text='-')
        self.LabelSplitRangeTo.pack(padx='2', pady='4', side='left')
        self.EntrySplitRangeStop = ttk.Entry(self.FrameSplitMode)
        self.split_range_stop = tk.IntVar(value='')
        self.EntrySplitRangeStop.configure(
                justify='center', state='disabled', textvariable=self.split_range_stop, validate='focusout'
                )
        self.EntrySplitRangeStop.configure(width='5')
        self.EntrySplitRangeStop.pack(padx='4', pady='4', side='left')
        self.EntrySplitRangeStop.configure(validatecommand=self.valid_stop)
        self.FrameSplitMode.configure(height='200', width='200')
        self.FrameSplitMode.pack(fill='x', side='top')
        self.FrameOption.configure(height='200', text=_('Option'), width='200')
        self.FrameOption.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.process_info = tk.StringVar(value='')
        self.LabelProcessInfo.configure(textvariable=self.process_info)
        self.LabelProcessInfo.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text=_('Split'))
        self.ButtonProcess.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text=_('Split PDF'), width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def get_pdf_file(self):
        pass

    def set_split_pdf_dir(self):
        pass

    def set_split_mode(self):
        pass

    def valid_page(self):
        pass

    def valid_start(self):
        pass

    def valid_stop(self):
        pass

    def process(self):
        pass
