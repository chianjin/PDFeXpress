from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class MergePdfFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(
            master,
            function_id='merge_pdf',
        )

    def _set_input_frame(self):
        self.file_list_view = FileListView(self.input_frame)
        self.file_list_view.pack(fill=tk.BOTH, expand=True)
        self._setup_auto_output()

    def _set_options_frame(self):
        self._generate_bookmarks = tk.BooleanVar(value=True)
        self._double_side_print = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.options_frame,
            text='生成书签',
            variable=self._generate_bookmarks,
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            self.options_frame,
            text='双面打印',
            variable=self._double_side_print,
        ).pack(side=tk.LEFT, padx=(10, 0))

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
            output_name = f"{first_file.stem}_合并.pdf"
            output_path = first_file.parent / output_name
            self.output_path_picker.set_path(output_path)

        first_file_var.trace_add('write', update_output)

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_file_paths()

    def get_options(self) -> dict:
        return {
            'generate_bookmarks': self._generate_bookmarks.get(),
            'double_side_print': self._double_side_print.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    frame = MergePdfFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    root.mainloop()
