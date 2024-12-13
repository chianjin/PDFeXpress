import tkinter as tk
from tkinter import ttk

from app import (
    MergePDF, RotatePDF, ExtractText, ExtractImage,
    ImageToPDF, SplitPDF, MergeInvoice, PDFToImage,
    CompressPDF
)
from constant import SYSTEM, APPLICATION_NAME


class MainFrame(tk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self._current_action = 'merge_pdf'

        self.FrameLeft = ttk.Frame(master=self)
        self._actions = {
            'merge_pdf': [_('Merge PDF'), MergePDF(self)],
            'split_pdf': [_('Split PDF'), SplitPDF(self)],
            'rotate_pdf': [_('Rotate PDF'), RotatePDF(self)],
            # 'compress_pdf': [_('Compress PDF'), CompressPDF(self)],
            'extract_text': [_('Extract Text'), ExtractText(self)],
            'extract_image': [_('Extract Image'), ExtractImage(self)],
            'image_to_pdf': [_('Image to PDF'), ImageToPDF(self)],
            'pdf_to_image': [_('PDF to Image'), PDFToImage(self)],
            'merge_invoice': [_('Merge Invoice'), MergeInvoice(self)],
        }
        for action in self._actions.keys():
            button = ttk.Button(
                master=self.FrameLeft,
                text=self._actions[action][0],
                command=lambda wid=action: self.set_action(wid)
            )
            button.pack(fill='x', ipadx=2, padx=4, pady=4)
            self._actions[action].append(button)
            if action == self._current_action:
                button.configure(state='disabled')

        self.FrameLeft.pack(side='left', fill='y', padx=4, pady=4)
        self._actions[self._current_action][1].pack(expand=True, fill='both', padx=4, pady=4)

    def set_action(self, action):
        self._actions[self._current_action][1].pack_forget()
        self._actions[self._current_action][2].configure(state='normal')
        self._actions[action][1].pack(expand=True, fill='both', padx=4, pady=4)
        self._actions[action][2].configure(state='disabled')
        self._current_action = action


if __name__ == '__main__':
    if SYSTEM == 'Windows':
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(True)

    root = tk.Tk()
    root.title(APPLICATION_NAME)
    main_frame = MainFrame(root)
    main_frame.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
