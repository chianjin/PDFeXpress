from pathlib import Path
import tkinter as tk
from tkinter import ttk

from config import ICONS_PATH, PAGE_RANGE_SYNTEX
from ui.components import HelpWindow, PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class SplitPdfFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='split_pdf', output_mode='folder')

        self.help_window = None

    def _set_input_frame(self):
        """创建输入文件框架"""
        self.input_path_picker = PathPicker(self.input_frame, mode='open')
        self.input_path_picker.pack(side=tk.TOP, fill=tk.X)
        self.input_path_picker.set_trace('write', self._set_output_path)

    def _set_options_frame(self):
        """创建选项框架"""

        self.split_mode = tk.StringVar(value='singel')
        # 跟踪拆分模式，决定输入框是否可用
        self.split_mode.trace_add('write', self._set_split_value_entry_state)
        self.split_value = tk.StringVar()

        # 选项
        radio_frame = ttk.Frame(self.options_frame)
        radio_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Radiobutton(
            radio_frame,
            text='单页',
            value='singel',
            variable=self.split_mode,
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            radio_frame,
            text='按页数',
            value='pages',
            variable=self.split_mode,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            radio_frame,
            text='按份数',
            value='copies',
            variable=self.split_mode,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            radio_frame,
            text='自定义范围',
            value='range',
            variable=self.split_mode,
        ).pack(side=tk.LEFT, padx=(5, 0))

        self.split_value_entry = ttk.Entry(
            radio_frame,
            textvariable=self.split_value,
            state=tk.DISABLED,
        )
        self.split_value_entry.pack(side=tk.LEFT, padx=(5, 0))
        # 帮助
        help_frame = ttk.Frame(self.options_frame)
        help_frame.pack(side=tk.TOP, pady=(5, 0))
        self._help_icon = tk.PhotoImage(file=ICONS_PATH / 'help.png')
        ttk.Label(
            help_frame,
            text='提示: 按页数、按份数输入整数，例如 2；自定义范围示例：1-5;7-12。点击',
        ).pack(side=tk.LEFT)
        ttk.Button(
            help_frame,
            image=self._help_icon,
            style='Toolbutton',
            command=self._show_help_window,
        ).pack(side=tk.LEFT)
        ttk.Label(
            help_frame,
            text='查看详细语法。',
        ).pack(side=tk.LEFT)

    def _set_output_path(self, *_args):
        """设置输出路径（仅在 auto_output 启用时）"""
        if not self.output_path_picker.is_auto_output_enabled():
            return

        input_path = self.input_path_picker.get_path()
        if input_path and input_path.exists():
            self.output_path_picker.set_path(input_path.parent)

    def _set_split_value_entry_state(self):
        """设置 split_value 的状态"""
        if self.split_mode.get() == 'singel':
            self.split_value_entry.configure(state=tk.DISABLED)
        else:
            self.split_value_entry.configure(state=tk.NORMAL)

    def _show_help_window(self):
        """显示帮助窗口"""
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.lift()
            return

        with PAGE_RANGE_SYNTEX.open('r', encoding='utf-8') as help_file:
            help_title = help_file.readline()
            help_file.seek(0)
            help_text = help_file.read()

        self.help_window = HelpWindow(self, help_title, help_text)
        self.help_window.focus()

    def get_input_files(self) -> tuple[Path]:
        """获取输入文件列表"""
        return (self.input_path_picker.get_path(),)

    def get_options(self) -> dict:
        """获取选项"""
        split_mode = self.split_mode.get()
        split_value = self.split_value.get()
        return {
            'split_mode': split_mode,
            'split_value': split_value,
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    frame = SplitPdfFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    root.update_idletasks()
    root.mainloop()
