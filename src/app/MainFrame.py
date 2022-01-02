import tkinter as tk
from collections import namedtuple

from app.ExtractImages import ExtractImages
from app.ExtractText import ExtractText
from app.FrameMenu import FrameMenu
from app.Images2PDF import Images2PDF
from app.MergePDF import MergePDF
from app.PDF2Images import PDF2Images
from app.RotatePDF import RotatePDF
from app.SplitPDF import SplitPDF
from ui.UiMainFrame import UiMainFrame

operate = namedtuple('operate', ('frame', 'button'))


class MainFrame(UiMainFrame):
    def __init__(self, master=None, **kw):
        super(MainFrame, self).__init__(master=master, **kw)

        self._operates = {
                'ButtonMergePDF': operate(MergePDF(master=self.FrameOperate), self.ButtonMergePDF),
                'ButtonSplitPDF': operate(SplitPDF(master=self.FrameOperate), self.ButtonSplitPDF),
                'ButtonRotatePDF': operate(RotatePDF(master=self.FrameOperate), self.ButtonRotatePDF),
                'ButtonExtractImages': operate(ExtractImages(master=self.FrameOperate), self.ButtonExtractImages),
                'ButtonExtractText': operate(ExtractText(master=self.FrameOperate), self.ButtonExtractText),
                'ButtonPDF2Images': operate(PDF2Images(master=self.FrameOperate), self.ButtonPDF2Images),
                'ButtonImages2PDF': operate(Images2PDF(master=self.FrameOperate), self.ButtonImages2PDF)
                }

        self._current_operate = 'ButtonMergePDF'
        current_operate = self._operates.get(self._current_operate)
        current_operate.frame.pack(side='top', expand=True, fill='both')

        self.master.configure(menu=FrameMenu(self.master))

    def set_operate(self, widget_id):
        if widget_id != self._current_operate:
            self._operates.get(self._current_operate).frame.pack_forget()
            self._current_operate = widget_id
            self._operates.get(self._current_operate).frame.pack(side='top', expand=True, fill='both')


if __name__ == '__main__':
    root = tk.Tk()
    root.minsize(700, 500)
    menu = FrameMenu(root)
    root.configure(menu=menu)
    widget = MainFrame(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
