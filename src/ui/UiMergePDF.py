import tkinter as tk
import tkinter.ttk as ttk

from constants import TRANSLATER as _


class UiMergePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiMergePDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='{Microsoft YaHei UI} 16 {bold}', text=_('Merge PDF'))
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='10', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FramePDFList = ttk.Labelframe(self)
        self.TreeViewPDFList = ttk.Treeview(self.FramePDFList)
        self.TreeViewPDFList_cols = ['ColumnDirName', 'ColumnFileName']
        self.TreeViewPDFList_dcols = ['ColumnDirName', 'ColumnFileName']
        self.TreeViewPDFList.configure(columns=self.TreeViewPDFList_cols, displaycolumns=self.TreeViewPDFList_dcols)
        self.TreeViewPDFList.column('ColumnDirName', anchor='w', stretch='true', width='150', minwidth='20')
        self.TreeViewPDFList.column('ColumnFileName', anchor='w', stretch='true', width='300', minwidth='20')
        self.TreeViewPDFList.heading('ColumnDirName', anchor='w', text=_('Folder'))
        self.TreeViewPDFList.heading('ColumnFileName', anchor='w', text=_('File Name'))
        self.TreeViewPDFList.pack(expand='true', fill='both', padx='4', pady='4', side='left')
        self.ScrollbarPDFList = ttk.Scrollbar(self.FramePDFList)
        self.ScrollbarPDFList.configure(orient='vertical')
        self.ScrollbarPDFList.pack(fill='y', side='left')
        self.ButtonAddPDF = ttk.Button(self.FramePDFList)
        self.ButtonAddPDF.configure(text=_('Add PDF'))
        self.ButtonAddPDF.pack(fill='x', padx='4', pady='4', side='top')
        self.ButtonAddPDF.configure(command=self.add_pdf)
        self.ButtonRemovePDF = ttk.Button(self.FramePDFList)
        self.ButtonRemovePDF.configure(text=_('Remove PDF'))
        self.ButtonRemovePDF.pack(fill='x', padx='4', pady='4', side='top')
        self.ButtonRemovePDF.configure(command=self.remove_pdf)
        self.ButtonRemoveAll = ttk.Button(self.FramePDFList)
        self.ButtonRemoveAll.configure(text=_('Remove All'))
        self.ButtonRemoveAll.pack(fill='x', padx='4', pady='4', side='top')
        self.ButtonRemoveAll.configure(command=self.remove_all)
        self.ButtonMoveTop = ttk.Button(self.FramePDFList)
        self.ButtonMoveTop.configure(text=_('Move to First'))
        self.ButtonMoveTop.pack(fill='x', padx='4', pady='4', side='top')
        self.ButtonMoveTop.configure(command=self.move_top)
        self.ButtonMoveUp = ttk.Button(self.FramePDFList)
        self.ButtonMoveUp.configure(text=_('Move Up'))
        self.ButtonMoveUp.pack(fill='x', padx='4', pady='4', side='top')
        self.ButtonMoveUp.configure(command=self.move_up)
        self.ButtonMoveDown = ttk.Button(self.FramePDFList)
        self.ButtonMoveDown.configure(text=_('Move Down'))
        self.ButtonMoveDown.pack(fill='x', padx='4', pady='4', side='top')
        self.ButtonMoveDown.configure(command=self.move_down)
        self.ButtonMoveBottom = ttk.Button(self.FramePDFList)
        self.ButtonMoveBottom.configure(text=_('Move to Last'))
        self.ButtonMoveBottom.pack(fill='x', padx='4', pady='4', side='top')
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
        self.ButtonMergedPDFFile.pack(padx='4', pady='4', side='left')
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
        self.ButtonProcess.pack(padx='4', pady='4', side='left')
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
