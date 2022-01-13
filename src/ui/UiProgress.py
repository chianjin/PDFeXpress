import tkinter as tk
import tkinter.ttk as ttk

from constants import TRANSLATER as _


class UiProgress(tk.Toplevel):
    def __init__(self, master=None, **kw):
        super(UiProgress, self).__init__(master, **kw)
        self.Frame = ttk.Frame(self)
        self.FrameInfo = ttk.Frame(self.Frame)
        self.LabelAppInfo = ttk.Label(self.FrameInfo)
        self.app_info = tk.StringVar(value='')
        self.LabelAppInfo.configure(compound='top', textvariable=self.app_info)
        self.LabelAppInfo.pack(padx='20', side='left')
        self.LabelProcessInfo = ttk.Label(self.FrameInfo)
        self.process_info = tk.StringVar(value='')
        self.LabelProcessInfo.configure(textvariable=self.process_info)
        self.LabelProcessInfo.pack(side='left')
        self.FrameInfo.configure(height='200', width='200')
        self.FrameInfo.pack(fill='x', pady='20', side='top')
        self.Progressbar = ttk.Progressbar(self.Frame)
        self.progress = tk.IntVar(value='')
        self.Progressbar.configure(length='400', orient='horizontal', variable=self.progress)
        self.Progressbar.pack(fill='y', padx='20', side='top')
        self.ButtonStop = ttk.Button(self.Frame)
        self.ButtonStop.configure(text=_('Stop'))
        self.ButtonStop.pack(ipadx='2', pady='20', side='top')
        self.ButtonStop.configure(command=self.stop_process)
        self.Frame.configure(height='400', width='500')
        self.Frame.pack(expand='true', fill='both', side='top')

    def stop_process(self):
        pass
