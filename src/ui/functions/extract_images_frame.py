from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class ExtractImagesFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='extract_images', output_mode='folder')

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)
        self._setup_auto_output()

    def _set_options_frame(self):
        self._ignore_small = tk.BooleanVar(value=True)
        self._min_width = tk.IntVar(value=100)
        self._min_height = tk.IntVar(value=100)

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Checkbutton(
            options_frame,
            text='忽略小图像',
            variable=self._ignore_small,
        ).pack(side=tk.LEFT, anchor=tk.W)

        ttk.Label(options_frame, text='最小宽度:').pack(side=tk.LEFT, padx=(10, 0))
        self.width_entry = ttk.Entry(
            options_frame,
            textvariable=self._min_width,
            width=8,
        )
        self.width_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(options_frame, text='px').pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(options_frame, text='最小高度:').pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(
            options_frame,
            textvariable=self._min_height,
            width=8,
        )
        self.height_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(options_frame, text='px').pack(side=tk.LEFT, padx=(2, 0))

        self._ignore_small.trace_add('write', self._update_size_entry_state)

    def _update_size_entry_state(self, *_args):
        if self._ignore_small.get():
            self.width_entry.configure(state=tk.NORMAL)
            self.height_entry.configure(state=tk.NORMAL)
        else:
            self.width_entry.configure(state=tk.DISABLED)
            self.height_entry.configure(state=tk.DISABLED)

    def _setup_auto_output(self):
        first_file_var = self.file_list_view.get_first_file_var()

        def update_output(*_args):
            if not self.output_path_picker.is_auto_output_enabled():
                return

            first_file_str = first_file_var.get()
            if not first_file_str:
                self.output_path_picker.path.set('')
                return

            first_file = Path(first_file_str)
            self.output_path_picker.set_path(first_file.parent)

        first_file_var.trace_add('write', update_output)

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_file_paths()

    def get_options(self) -> dict:
        return {
            'ignore_small': self._ignore_small.get(),
            'min_width': self._min_width.get(),
            'min_height': self._min_height.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    frame = ExtractImagesFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    root.mainloop()
