from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class RotatePdfFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='rotate_pdf', output_mode='folder')

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _set_options_frame(self):
        self._rotation_angle = tk.IntVar(value=90)

        angle_frame = ttk.Frame(self.options_frame)
        angle_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(angle_frame, text='顺时针').pack(side=tk.LEFT)
        ttk.Radiobutton(
            angle_frame,
            text='90°',
            value=90,
            variable=self._rotation_angle,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            angle_frame,
            text='180°',
            value=180,
            variable=self._rotation_angle,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            angle_frame,
            text='270°',
            value=270,
            variable=self._rotation_angle,
        ).pack(side=tk.LEFT, padx=(5, 0))

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_file_paths()

    def get_options(self) -> dict:
        return {
            'rotation_angle': self._rotation_angle.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    frame = RotatePdfFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    root.mainloop()
