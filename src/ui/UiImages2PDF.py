import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiImages2PDF.ui"


class UiImages2PDF(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(UiImages2PDF, self).__init__(master, **kw)
        self.FrameTitle = ttk.Frame(self)
        self.LabelFrameName = ttk.Label(self.FrameTitle)
        self.frame_name = tk.StringVar(value='图像转换为 PDF')
        self.LabelFrameName.configure(
            font='{Microsoft YaHei UI} 16 {bold}', text='图像转换为 PDF', textvariable=self.frame_name
            )
        self.LabelFrameName.pack(side='left')
        self.FrameTitle.configure(height='200', padding='10', width='200')
        self.FrameTitle.pack(fill='x', side='top')
        self.FrameImageList = ttk.Labelframe(self)
        self.TreeViewImageList = ttk.Treeview(self.FrameImageList)
        self.TreeViewImageList_cols = ['ColumnDirname', 'ColumnFilename']
        self.TreeViewImageList_dcols = ['ColumnDirname', 'ColumnFilename']
        self.TreeViewImageList.configure(
            columns=self.TreeViewImageList_cols, displaycolumns=self.TreeViewImageList_dcols
            )
        self.TreeViewImageList.column('ColumnDirname', anchor='w', stretch='true', width='150', minwidth='20')
        self.TreeViewImageList.column('ColumnFilename', anchor='w', stretch='true', width='300', minwidth='20')
        self.TreeViewImageList.heading('ColumnDirname', anchor='w', text='目录名')
        self.TreeViewImageList.heading('ColumnFilename', anchor='w', text='文件名')
        self.TreeViewImageList.pack(expand='true', fill='both', padx='4', pady='4', side='left')
        self.ScrollbarImagesList = ttk.Scrollbar(self.FrameImageList)
        self.ScrollbarImagesList.configure(orient='vertical')
        self.ScrollbarImagesList.pack(fill='y', side='left')
        self.ButtonAddImages = ttk.Button(self.FrameImageList)
        self.ButtonAddImages.configure(text='添加图像')
        self.ButtonAddImages.pack(padx='4', pady='4', side='top')
        self.ButtonAddImages.configure(command=self.add_images)
        self.ButtonRemoveImage = ttk.Button(self.FrameImageList)
        self.ButtonRemoveImage.configure(text='移除图像')
        self.ButtonRemoveImage.pack(padx='4', pady='4', side='top')
        self.ButtonRemoveImage.configure(command=self.remove_images)
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
        self.FrameImageList.configure(height='200', text='图像列表', width='200')
        self.FrameImageList.pack(expand='true', fill='both', padx='4', pady='4', side='top')
        self.FramePDFFile = ttk.Labelframe(self)
        self.EntryPDFFile = ttk.Entry(self.FramePDFFile)
        self.pdf_file = tk.StringVar(value='')
        self.EntryPDFFile.configure(state='readonly', textvariable=self.pdf_file)
        self.EntryPDFFile.pack(expand='true', fill='x', padx='4', pady='4', side='left')
        self.ButtonPDFFile = ttk.Button(self.FramePDFFile)
        self.ButtonPDFFile.configure(text='浏览')
        self.ButtonPDFFile.pack(padx='4', pady='4', side='left')
        self.ButtonPDFFile.configure(command=self.set_pdf_file)
        self.FramePDFFile.configure(height='200', text='PDF 文件', width='200')
        self.FramePDFFile.pack(fill='x', padx='4', pady='4', side='top')
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
        self.ButtonProcess.configure(state='disabled', text='转换')
        self.ButtonProcess.pack(padx='4', pady='4', side='left')
        self.ButtonProcess.configure(command=self.process)
        self.FrameProcess.configure(height='200', text='转换图像', width='200')
        self.FrameProcess.pack(fill='x', padx='4', pady='4', side='top')

    def add_images(self):
        pass

    def remove_images(self):
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

    def set_pdf_file(self):
        pass

    def process(self):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiImages2PDF(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
