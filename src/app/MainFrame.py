from collections import namedtuple

from app.CompressPDF import CompressPDF
from app.ExtractImages import ExtractImages
from app.ExtractText import ExtractText
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

        self.FrameOperateButtons.configure(text=_('Operate'))

        self._operates = {
                'ButtonMergePDF': operate(MergePDF(master=self), self.ButtonMergePDF),
                'ButtonSplitPDF': operate(SplitPDF(master=self), self.ButtonSplitPDF),
                'ButtonRotatePDF': operate(RotatePDF(master=self), self.ButtonRotatePDF),
                'ButtonCompressPDF': operate(CompressPDF(master=self), self.ButtonCompressPDF),
                'ButtonExtractImages': operate(ExtractImages(master=self), self.ButtonExtractImages),
                'ButtonExtractText': operate(ExtractText(master=self), self.ButtonExtractText),
                'ButtonPDF2Images': operate(PDF2Images(master=self), self.ButtonPDF2Images),
                'ButtonImages2PDF': operate(Images2PDF(master=self), self.ButtonImages2PDF)
                }

        self._current_operate = 'ButtonMergePDF'
        current_operate = self._operates.get(self._current_operate)
        current_operate.button.configure(state='disabled')
        current_operate.frame.pack(side='top', expand=True, fill='both')

    def set_operate(self, widget_id):
        old_operate = self._operates.get(self._current_operate)
        old_operate.frame.pack_forget()
        old_operate.button.configure(state='normal')

        self._current_operate = widget_id
        current_operate = self._operates.get(self._current_operate)
        current_operate.frame.pack(side='top', expand=True, fill='both')
        current_operate.button.configure(state='disabled')
