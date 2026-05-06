from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class ExtractTextFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='extract_text', output_mode='folder')

    def _set_input_frame(self):
        self.file_list_view = FileListView(self.input_frame)
        self.file_list_view.pack(fill=tk.BOTH, expand=True)
        self._setup_auto_output()

    def _set_options_frame(self):
        self._output_format = tk.StringVar(value='txt')
        self._rebuild_order = tk.BooleanVar(value=False)

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(options_frame, text='输出格式').pack(side=tk.LEFT)
        ttk.Radiobutton(
            options_frame,
            text='TXT',
            value='txt',
            variable=self._output_format,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            options_frame,
            text='HTML',
            value='html',
            variable=self._output_format,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            options_frame,
            text='JSON',
            value='json',
            variable=self._output_format,
        ).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Checkbutton(
            options_frame,
            text='重建阅读顺序',
            variable=self._rebuild_order,
        ).pack(side=tk.LEFT, padx=(15, 0))

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
            'output_format': self._output_format.get(),
            'rebuild_order': self._rebuild_order.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    frame = ExtractTextFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    root.mainloop()
