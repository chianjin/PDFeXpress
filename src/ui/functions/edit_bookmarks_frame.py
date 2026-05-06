from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.path_picker import PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class EditBookmarksFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='edit_bookmarks', output_mode='save')

    def _set_input_frame(self):
        self.input_path_picker = PathPicker(self.input_frame, mode='open')
        self.input_path_picker.pack(side=tk.TOP, fill=tk.X)

    def _get_auto_output_strategy(self):
        from utils.auto_output_helpers import setup_auto_output_single_to_single

        return lambda frame: setup_auto_output_single_to_single(
            frame.input_path_picker,
            frame.output_path_picker,
            path_generator=lambda input_path: input_path.parent / f'{input_path.stem}_书签.pdf',
        )

    def _set_options_frame(self):
        self._level = tk.StringVar()
        self._page = tk.StringVar()
        self._title = tk.StringVar()

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(options_frame, text='层级：').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._level,
            width=8,
        ).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(options_frame, text='页码：').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._page,
            width=8,
        ).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(options_frame, text='标题：').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._title,
            width=30,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        button_frame = ttk.Frame(self.options_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        ttk.Button(
            button_frame,
            text='编辑',
            width=10,
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            button_frame,
            text='添加',
            width=10,
        ).pack(side=tk.RIGHT)

    def get_input_files(self) -> list[Path]:
        input_path = self.input_path_picker.get()
        if input_path:
            return [Path(input_path)]
        return []

    def get_options(self) -> dict:
        return {
            'level': self._level.get(),
            'page': self._page.get(),
            'title': self._title.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = EditBookmarksFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
