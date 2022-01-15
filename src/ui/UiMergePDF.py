import tkinter as tk
import tkinter.ttk as ttk


class UiMergePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiMergePDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='{Microsoft YaHei UI} 20 {bold}', text=_('Merge PDF'))
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='20', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FramePDFList = ttk.Labelframe(self)
        self.TreeViewPDFList = ttk.Treeview(self.FramePDFList)
        _columns = ['dir_name', 'file_name', 'file_path']
        _display_columns = ['dir_name', 'file_name']
        self.TreeViewPDFList.configure(columns=_columns, displaycolumns=_display_columns, show='headings')
        self.TreeViewPDFList.column('dir_name', anchor='w', stretch='true', width='150', minwidth='20')
        self.TreeViewPDFList.column('file_name', anchor='w', stretch='true', width='300', minwidth='20')
        self.TreeViewPDFList.heading('dir_name', anchor='w', text=_('Folder'))
        self.TreeViewPDFList.heading('file_name', anchor='w', text=_('File Name'))
        self.TreeViewPDFList.pack(expand='true', fill='both', padx='4', pady='4', side='left')
        self.ScrollbarPDFList = ttk.Scrollbar(self.FramePDFList)
        self.ScrollbarPDFList.configure(orient='vertical')
        self.ScrollbarPDFList.pack(fill='y', pady='4', side='left')
        self.ButtonAddPDF = ttk.Button(self.FramePDFList)
        self.ButtonAddPDF.configure(text=_('Add PDF'))
        self.ButtonAddPDF.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')
        self.ButtonAddPDF.configure(command=self.add_pdf)
        self.ButtonRemovePDF = ttk.Button(self.FramePDFList)
        self.ButtonRemovePDF.configure(text=_('Remove PDF'))
        self.ButtonRemovePDF.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')
        self.ButtonRemovePDF.configure(command=self.remove_pdf)
        self.ButtonRemoveAll = ttk.Button(self.FramePDFList)
        self.ButtonRemoveAll.configure(text=_('Remove All'))
        self.ButtonRemoveAll.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')
        self.ButtonRemoveAll.configure(command=self.remove_all)
        self.Separator = ttk.Separator(self.FramePDFList)
        self.Separator.configure(orient='horizontal')
        self.Separator.pack(fill='x', padx='4', pady='8', side='top')
        self.ButtonMoveTop = ttk.Button(self.FramePDFList)
        self.ButtonMoveTop.configure(text=_('Move to First'))
        self.ButtonMoveTop.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')
        self.ButtonMoveTop.configure(command=self.move_top)
        self.ButtonMoveUp = ttk.Button(self.FramePDFList)
        self.ButtonMoveUp.configure(text=_('Move Up'))
        self.ButtonMoveUp.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')
        self.ButtonMoveUp.configure(command=self.move_up)
        self.ButtonMoveDown = ttk.Button(self.FramePDFList)
        self.ButtonMoveDown.configure(text=_('Move Down'))
        self.ButtonMoveDown.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')
        self.ButtonMoveDown.configure(command=self.move_down)
        self.ButtonMoveBottom = ttk.Button(self.FramePDFList)
        self.ButtonMoveBottom.configure(text=_('Move to Last'))
        self.ButtonMoveBottom.pack(fill='x', ipadx='2', padx='4', pady='4', side='top')
        self.ButtonMoveBottom.configure(command=self.move_bottom)
        self.FramePDFList.configure(height='200', text=_('PDF List'), width='200')
        self.FramePDFList.pack(expand='true', fill='both', padx='4', pady='4', side='top')
        self.FrameMergedPDFFile = ttk.Labelframe(self)
        self.EntryMergedPDFFile = ttk.Entry(self.FrameMergedPDFFile)
        self.merged_pdf_file = tk.StringVar(value='')
        self.EntryMergedPDFFile.configure(state='readonly', textvariable=self.merged_pdf_file)
        self.EntryMergedPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonMergedPDFFile = ttk.Button(self.FrameMergedPDFFile)
        self.ButtonMergedPDFFile.configure(text=_('Browser'))
        self.ButtonMergedPDFFile.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonMergedPDFFile.configure(command=self.set_merged_pdf_file)
        self.FrameMergedPDFFile.configure(height='200', text=_('Merged PDF File'), width='200')
        self.FrameMergedPDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.LabelProcessInfo.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text=_('Merge'))
        self.ButtonProcess.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text=_('Merge PDF'), width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def add_pdf(self):
        pass

    def remove_pdf(self):
        pass

    def remove_all(self):
        pass

    def move_top(self):
        pass

    def move_up(self):
        pass

    def move_down(self):
        pass

    def move_bottom(self):
        pass

    def set_merged_pdf_file(self):
        pass

    def process(self):
        pass
