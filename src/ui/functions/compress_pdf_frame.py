from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class CompressPdfFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='compress_pdf', output_mode='folder')

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _get_auto_output_strategy(self):
        from utils.auto_output_helpers import setup_auto_output_list_to_folder

        return lambda frame: setup_auto_output_list_to_folder(
            frame.file_list_view,
            frame.output_path_picker,
        )

    def _set_options_frame(self):
        self._compress_images = tk.BooleanVar(value=False)
        self._max_resolution = tk.IntVar(value=150)

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Checkbutton(
            options_frame,
            text='压缩图片',
            variable=self._compress_images,
            command=self._on_compress_images_toggle,
        ).pack(side=tk.LEFT)

        ttk.Label(options_frame, text='最大分辨率：').pack(side=tk.LEFT, padx=(10, 0))
        self._resolution_spinbox = ttk.Spinbox(
            options_frame,
            from_=72,
            to=600,
            increment=10,
            textvariable=self._max_resolution,
            state=tk.DISABLED,
            width=10,
        )
        self._resolution_spinbox.pack(side=tk.LEFT)
        ttk.Label(options_frame, text='DPI').pack(side=tk.LEFT, padx=(5, 0))

    def _on_compress_images_toggle(self):
        """压缩图片复选框切换时的处理"""
        if self._compress_images.get():
            result = messagebox.askyesno(
                '确认',
                '压缩图片将非常耗时，确定要压缩图片吗？',
            )
            if not result:
                self._compress_images.set(False)
                return

        # 根据是否选中压缩图片，启用/禁用分辨率输入
        if self._compress_images.get():
            self._resolution_spinbox.configure(state=tk.NORMAL)
        else:
            self._resolution_spinbox.configure(state=tk.DISABLED)

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_files()

    def get_options(self) -> dict:
        return {
            'compress_images': self._compress_images.get(),
            'max_resolution': self._max_resolution.get() if self._compress_images.get() else None,
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = CompressPdfFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
