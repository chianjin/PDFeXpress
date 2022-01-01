import pathlib
import tkinter as tk
import tkinter.ttk as ttk

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UiAbort.ui"


class UiAbout(tk.Toplevel):
    def __init__(self, master=None, **kw):
        super(UiAbout, self).__init__(master, **kw)
        self.FrameAbout = ttk.Frame(self)
        self.LabelAppName = ttk.Label(self.FrameAbout)
        self.app_name = tk.StringVar(value='PDF Express')
        self.LabelAppName.configure(font='{Arial} 36 {bold}', text='PDF Express', textvariable=self.app_name)
        self.LabelAppName.pack(padx='40', pady='40', side='top')
        self.FrameVersion = ttk.Frame(self.FrameAbout)
        self.LabelAppVersionText = ttk.Label(self.FrameVersion)
        self.LabelAppVersionText.configure(font='{Arial} 14 {}', text='Version')
        self.LabelAppVersionText.pack(padx='5', side='left')
        self.LabelAppVersion = ttk.Label(self.FrameVersion)
        self.app_version = tk.StringVar(value='0.1-BETA-1')
        self.LabelAppVersion.configure(font='{Arial} 14 {}', text='0.1-BETA-1', textvariable=self.app_version)
        self.LabelAppVersion.pack(padx='5', side='top')
        self.FrameVersion.configure(height='200', width='200')
        self.FrameVersion.pack(side='top')
        self.LabelUrl = ttk.Label(self.FrameAbout)
        self.app_url = tk.StringVar(value='https://github.com/chianjin/PDFExpress')
        self.LabelUrl.configure(
                cursor='hand2', font='{Arial} 10 {underline}', foreground='#0000ff',
                text='https://github.com/chianjin/PDFExpress'
                )
        self.LabelUrl.configure(textvariable=self.app_url)
        self.LabelUrl.pack(pady='40', side='top')
        self.LabelUrl.bind('<Button-1>', self.open_url, add='')
        self.FrameAbout.configure(height='200', width='200')
        self.FrameAbout.pack(side='top')

    def open_url(self, event=None):
        pass


if __name__ == '__main__':
    root = tk.Tk()
    widget = UiAbout(root)
    widget.pack(expand=True, fill='both')
    root.mainloop()
