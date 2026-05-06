from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.path_picker import PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame
from utils.file_types import FILE_TYPES


class PdfToLongImageFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(
            master,
            function_id='pdf_to_long_image',
            output_mode='save',
            output_file_types=FILE_TYPES['JPEG'],
            output_default_extension='.jpg',
        )

    def _set_input_frame(self):
        self.input_path_picker = PathPicker(self.input_frame, mode='open')
        self.input_path_picker.pack(side=tk.TOP, fill=tk.X)

    def _get_auto_output_strategy(self):
        from utils.auto_output_helpers import setup_auto_output_single_to_single

        return lambda frame: setup_auto_output_single_to_single(
            frame.input_path_picker,
            frame.output_path_picker,
            path_generator=lambda input_path: input_path.parent / f'{input_path.stem}.jpg',
        )

    def _set_options_frame(self):
        self._dpi = tk.IntVar(value=150)
        self._quality = tk.IntVar(value=75)

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(options_frame, text='DPI:').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._dpi,
            width=6,
        ).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(options_frame, text='质量:').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._quality,
            width=6,
        ).pack(side=tk.LEFT, padx=(5, 0))

    def get_input_files(self) -> list[Path]:
        input_path = self.input_path_picker.get()
        if input_path:
            return [Path(input_path)]
        return []

    def get_options(self) -> dict:
        return {
            'dpi': self._dpi.get(),
            'quality': self._quality.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = PdfToLongImageFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
