import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiMergePDF.ui"


class UiMergePDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiMergePDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.frame_name = tk.StringVar(value='合并 PDF')
        self.LabelFrameName.configure(
                font='{Microsoft YaHei UI} 16 {bold}', text='合并 PDF', textvariable=self.frame_name
                )
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='10', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FrameImageList = ttk.Labelframe(self)
        self.TreeViewPDFList = ttk.Treeview(self.FrameImageList)
        self.TreeViewPDFList_cols = ['ColumnDirName', 'ColumnFileName']
        self.TreeViewPDFList_dcols = ['ColumnDirName', 'ColumnFileName']
        self.TreeViewPDFList.configure(columns=self.TreeViewPDFList_cols, displaycolumns=self.TreeViewPDFList_dcols)
        self.TreeViewPDFList.column('ColumnDirName', anchor='w', stretch='true', width='150', minwidth='20')
        self.TreeViewPDFList.column('ColumnFileName', anchor='w', stretch='true', width='300', minwidth='20')
        self.TreeViewPDFList.heading('ColumnDirName', anchor='w', text='目录名')
        self.TreeViewPDFList.heading('ColumnFileName', anchor='w', text='文件名')
        self.TreeViewPDFList.pack(expand='true', fill='both', padx='4', pady='4', side='left')
        self.ButtonAddPDF = ttk.Button(self.FrameImageList)
        self.ButtonAddPDF.configure(text='添加 PDF')
        self.ButtonAddPDF.pack(padx='4', pady='4', side='top')
        self.ButtonAddPDF.configure(command=self.add_pdf)
        self.ButtonRemovePDF = ttk.Button(self.FrameImageList)
        self.ButtonRemovePDF.configure(text='移除 PDF')
        self.ButtonRemovePDF.pack(padx='4', pady='4', side='top')
        self.ButtonRemovePDF.configure(command=self.remove_pdf)
        self.ButtonRemoveAll = ttk.Button(self.FrameImageList)
        self.ButtonRemoveAll.configure(text='全部移除')
        self.ButtonRemoveAll.pack(padx='4', pady='4', side='top')
        self.ButtonRemoveAll.configure(command=self.remove_all)
        self.ButtonMoveTop = ttk.Button(self.FrameImageList)
        self.ButtonMoveTop.configure(text='移至顶部')
        self.ButtonMoveTop.pack(padx='4', pady='4', side='top')
        self.ButtonMoveTop.configure(command=self.move_top)
        self.ButtonMoveUp = ttk.Button(self.FrameImageList)
        self.ButtonMoveUp.configure(text='向上移动')
        self.ButtonMoveUp.pack(padx='4', pady='4', side='top')
        self.ButtonMoveUp.configure(command=self.move_up)
        self.ButtonMoveDown = ttk.Button(self.FrameImageList)
        self.ButtonMoveDown.configure(text='向下移动')
        self.ButtonMoveDown.pack(padx='4', pady='4', side='top')
        self.ButtonMoveDown.configure(command=self.move_down)
        self.ButtonMoveBottom = ttk.Button(self.FrameImageList)
        self.ButtonMoveBottom.configure(text='移至底部')
        self.ButtonMoveBottom.pack(padx='4', pady='4', side='top')
        self.ButtonMoveBottom.configure(command=self.move_bottom)
        self.FrameImageList.configure(height='200', text='PDF 列表', width='200')
        self.FrameImageList.pack(expand='true', fill='both', padx='4', pady='4', side='top')
        self.FrameMergedPDFFile = ttk.Labelframe(self)
        self.EntryMergedPDFFile = ttk.Entry(self.FrameMergedPDFFile)
        self.merged_pdf_file = tk.StringVar(value='')
        self.EntryMergedPDFFile.configure(textvariable=self.merged_pdf_file)
        self.EntryMergedPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonMergedPDFFile = ttk.Button(self.FrameMergedPDFFile)
        self.ButtonMergedPDFFile.configure(text='浏览')
        self.ButtonMergedPDFFile.pack(padx='4', pady='4', side='left')
        self.ButtonMergedPDFFile.configure(command=self.set_merged_pdf_file)
        self.FrameMergedPDFFile.configure(height='200', text='输出 PDF 文件', width='200')
        self.FrameMergedPDFFile.pack(fill='x', padx='4', pady='4', side='top')
        self.FrameProcess = ttk.Labelframe(self)
        self.LabelAppInfo = ttk.Label(self.FrameProcess)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='4', pady='4', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameProcess)
        self.LabelProcessInfo.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonProcess = ttk.Button(self.FrameProcess)
        self.ButtonProcess.configure(state='disabled', text='合并')
        self.ButtonProcess.pack(padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text='合并 PDF', width='200')
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


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiMergePDF(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
