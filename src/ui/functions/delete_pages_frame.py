from pathlib import Path
import tkinter as tk
from tkinter import ttk

from config import ICONS_PATH, PAGE_RANGE_SYNTAX
from ui.components import HelpWindow, PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class DeletePagesFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='delete_pages', output_mode='folder')

        self.help_window = None

    def _set_input_frame(self):
        self.input_path_picker = PathPicker(self.input_frame, mode='open')
        self.input_path_picker.pack(side=tk.TOP, fill=tk.X)

    def _get_auto_output_strategy(self):
        from utils.auto_output_helpers import setup_auto_output_single_to_folder

        return lambda frame: setup_auto_output_single_to_folder(
            frame.input_path_picker,
            frame.output_path_picker,
        )

    def _set_options_frame(self):
        self._page_range = tk.StringVar()
        self._help_icon = tk.PhotoImage(file=ICONS_PATH / 'help.png')

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(options_frame, text='删除页面范围：').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._page_range,
            width=30,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        ttk.Label(options_frame, text='示例：3,7-9,12;:2。点击').pack(side=tk.LEFT)
        ttk.Button(
            options_frame,
            image=self._help_icon,
            command=self._show_help,
            style='Toolbutton',
            padding=0,
        ).pack(side=tk.LEFT)
        ttk.Label(options_frame, text='查看详情。').pack(side=tk.LEFT)

    def _show_help(self):
        """显示页面范围规则帮助信息"""
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.lift()
            return

        with PAGE_RANGE_SYNTAX.open('r', encoding='utf-8') as f:
            help_title = f.readline().strip()
            f.seek(0)
            help_text = f.read()

        self.help_window = HelpWindow(self, title=help_title, content=help_text)
        self.help_window.focus()

    def get_input_files(self) -> list[Path]:
        input_path = self.input_path_picker.get()
        if input_path:
            return [Path(input_path)]
        return []

    def get_options(self) -> dict:
        return {
            'page_range': self._page_range.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = DeletePagesFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
