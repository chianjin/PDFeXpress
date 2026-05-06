from pathlib import Path
import tkinter as tk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class MergeInvoicesFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(
            master,
            function_id='merge_invoices',
        )

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _generate_output_filename(self, first_file: Path) -> str:
        return f'{first_file.stem}_合并发票.pdf'

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_file_paths()

    def get_options(self) -> dict:
        return {}


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = MergeInvoicesFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
