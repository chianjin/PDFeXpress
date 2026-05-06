from pathlib import Path
import tkinter as tk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class PdfToDocxFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='pdf_to_docx', output_mode='folder')

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _set_options_frame(self):
        self.options_frame.pack_forget()

    def _get_auto_output_strategy(self):
        from utils.auto_output_helpers import setup_auto_output_list_to_folder

        return lambda frame: setup_auto_output_list_to_folder(
            frame.file_list_view,
            frame.output_path_picker,
        )

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_files()

    def get_options(self) -> dict:
        return {}


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = PdfToDocxFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
