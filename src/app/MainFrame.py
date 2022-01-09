from collections import namedtuple

from app.CompressPDF import CompressPDF
from app.ExtractImages import ExtractImages
from app.ExtractText import ExtractText
from app.Images2PDF import Images2PDF
from app.MergePDF import MergePDF
from app.PDF2Images import PDF2Images
from app.RotatePDF import RotatePDF
from app.SplitPDF import SplitPDF
from constants import TRANSLATER as _
from ui.UiMainFrame import UiMainFrame

operate = namedtuple('operate', ('frame', 'button', 'text'))


class MainFrame(UiMainFrame):
    def __init__(self, master=None, **kw):
        super(MainFrame, self).__init__(master=master, **kw)

        self.FrameOperateButtons.configure(text=_('Operate'))

        self._operates = {
                'ButtonMergePDF': operate(MergePDF(master=self.FrameOperate), self.ButtonMergePDF, _('Merge PDF')),
                'ButtonSplitPDF': operate(SplitPDF(master=self.FrameOperate), self.ButtonSplitPDF, _('Split PDF')),
                'ButtonRotatePDF': operate(RotatePDF(master=self.FrameOperate), self.ButtonRotatePDF, _('Rotate PDF')),
                'ButtonCompressPDF': operate(
                    CompressPDF(master=self.FrameOperate), self.ButtonCompressPDF, _('Compress PDF')
                    ),
                'ButtonExtractImages': operate(
                    ExtractImages(master=self.FrameOperate), self.ButtonExtractImages, _('Extract Images')
                    ),
                'ButtonExtractText': operate(
                    ExtractText(master=self.FrameOperate), self.ButtonExtractText, _('Extract Text')
                    ),
                'ButtonPDF2Images': operate(
                    PDF2Images(master=self.FrameOperate), self.ButtonPDF2Images, _('PDF to Images')
                    ),
                'ButtonImages2PDF': operate(
                    Images2PDF(master=self.FrameOperate), self.ButtonImages2PDF, _('Images to PDF')
                    )
                }

        for _operate_name in self._operates:
            _operate = self._operates.get(_operate_name)
            _operate.button.configure(text=_operate.text)

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
