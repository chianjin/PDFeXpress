from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.components.path_picker import PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class AddWatermarkFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='add_watermark', output_mode='folder')

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _set_options_frame(self):
        self._watermark_text = tk.StringVar()
        self._invisible = tk.BooleanVar(value=False)

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(options_frame, text='水印文字:').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._watermark_text,
            width=20,
        ).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(options_frame, text='水印图片:').pack(side=tk.LEFT)
        self.watermark_image_picker = PathPicker(
            options_frame,
            mode='open',
        )
        self.watermark_image_picker.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Checkbutton(
            options_frame,
            text='隐水印',
            variable=self._invisible,
        ).pack(side=tk.LEFT)

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_files()

    def get_options(self) -> dict:
        return {
            'watermark_text': self._watermark_text.get(),
            'watermark_image': self.watermark_image_picker.path.get(),
            'invisible': self._invisible.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = AddWatermarkFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
