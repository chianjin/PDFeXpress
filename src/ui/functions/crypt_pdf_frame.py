from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class CryptPdfFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='crypt_pdf', output_mode='folder')

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _set_options_frame(self):
        self._password = tk.StringVar()
        self._mode = tk.StringVar(value='encrypt')

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(options_frame, text='密码:').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._password,
            width=20,
        ).pack(side=tk.LEFT, padx=(5, 15))

        ttk.Label(options_frame, text='模式:').pack(side=tk.LEFT)
        ttk.Radiobutton(
            options_frame,
            text='加密',
            value='encrypt',
            variable=self._mode,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            options_frame,
            text='解密',
            value='decrypt',
            variable=self._mode,
        ).pack(side=tk.LEFT, padx=(5, 0))

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_files()

    def get_options(self) -> dict:
        return {
            'password': self._password.get(),
            'mode': self._mode.get(),
        }

if __name__ == '__main__':
    from tkinterdnd2 import Tk
    root = Tk()
    app = CryptPdfFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
