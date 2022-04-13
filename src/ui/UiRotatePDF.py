import tkinter as tk
import tkinter.ttk as ttk


class UiRotatePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiRotatePDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.LabelFrameName.configure(font='FrameLabelFont', text=_('Rotate PDF'))
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='20', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FramePDFList = ttk.Labelframe(self)
        self.TreeViewPDFList = ttk.Treeview(self.FramePDFList)
        _columns = ['dir_name', 'file_name']
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

        self.FrameOption = ttk.Labelframe(self)
        self.LabelRotateDegree = ttk.Label(self.FrameOption)
        self.LabelRotateDegree.configure(text=_('Rotation Degree(Clockwise)'))
        self.LabelRotateDegree.pack(padx='4', pady='4', side='left')
        self.Radiobutton90 = ttk.Radiobutton(self.FrameOption)
        self.rotate_degree = tk.IntVar(value=90)
        self.Radiobutton90.configure(text='90°', value='90', variable=self.rotate_degree)
        self.Radiobutton90.pack(padx='4', pady='4', side='left')
        self.Radiobutton180 = ttk.Radiobutton(self.FrameOption)
        self.Radiobutton180.configure(text='180°', value='180', variable=self.rotate_degree)
        self.Radiobutton180.pack(padx='4', pady='4', side='left')
        self.Radiobutton270 = ttk.Radiobutton(self.FrameOption)
        self.Radiobutton270.configure(text='-90°', value='270', variable=self.rotate_degree)
        self.Radiobutton270.pack(padx='4', pady='4', side='left')
        self.FrameOption.configure(height='200', text=_('Option'), width='200')
        self.FrameOption.pack(fill='x', padx='4', pady='4', side='top')

        self.FrameOutputDir = ttk.Labelframe(self)
        self.EntryOutputDir = ttk.Entry(self.FrameOutputDir)
        self.output_dir = tk.StringVar(value='')
        self.EntryOutputDir.configure(state='disabled', textvariable=self.output_dir)
        self.EntryOutputDir.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonOutputDir = ttk.Button(self.FrameOutputDir)
        self.ButtonOutputDir.configure(text=_('Browser'))
        self.ButtonOutputDir.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonOutputDir.configure(command=self.set_output_dir)
        self.CheckButtonSourceDir = ttk.Checkbutton(self.FrameOutputDir)
        self.use_source_folder = tk.BooleanVar(value=True)
        self.CheckButtonSourceDir.configure(text=_('Source Folder'), variable=self.use_source_folder)
        self.CheckButtonSourceDir.configure(command=self.set_source_folder)
        self.CheckButtonSourceDir.pack(ipadx=4, ipady=4, side='right')
        self.FrameOutputDir.configure(height='200', text=_('Rotated PDF Folder'), width='200')
        self.FrameOutputDir.pack(fill='x', padx='4', pady='4', side='top')

        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.LabelProcessInfo.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text=_('Rotate'))
        self.ButtonProcess.pack(ipadx='2', padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text=_('Rotate PDF'), width='200')
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

    def set_output_dir(self):
        pass

    def set_source_folder(self):
        pass

    def process(self):
        pass
