from abc import ABC, abstractmethod
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Literal, final

from core.function_list import FUNCTION_LIST
from ui.components import ExecuteFrame, HeaderFrame, PathPicker
from utils import FILE_TYPES


class BaseFunctionFrame(ttk.Frame, ABC):
    def __init__(
        self,
        master,
        function_id='',
        output_mode: Literal['folder', 'save'] = 'save',
        output_file_types: list[tuple[str, str]] = FILE_TYPES['PDF'],
        output_default_extension: str = '.pdf',
    ):
        super().__init__(master, padding=5)
        self.master = master
        self.function_id = function_id
        self.output_mode = output_mode
        self.output_file_types = output_file_types
        self.output_default_extension = output_default_extension

        self.top_level = self.winfo_toplevel()

        self._setup_ui()
        self._set_input_frame()
        self._set_output_frame()
        self._set_options_frame()

    def _setup_ui(self):
        # 创建功能图标和标题的框架
        HeaderFrame(self, function_id=self.function_id).pack(side=tk.TOP, fill=tk.X, padx=10)

        # 创建输入文件框架
        self.input_frame = ttk.LabelFrame(self, text='PDF 文件', padding=5)
        self.input_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, pady=(5, 0))

        # 创建输出文件框架
        self.output_frame = ttk.LabelFrame(self, text='输出 PDF', padding=5)
        self.output_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        # 创建选项框架
        self.options_frame = ttk.LabelFrame(self, text='选项', padding=5)
        self.options_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        # 创建执行框架
        self.execute_frame = ExecuteFrame(self, FUNCTION_LIST[self.function_id].execute_text)
        self.execute_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

    @abstractmethod
    def _set_input_frame(self):
        """创建输入文件框架"""
        ttk.Label(self.input_frame, text='输入文件框架').pack(side=tk.TOP)
        pass

    @final
    def _set_output_frame(self):
        """创建输出文件框架"""

        if self.output_mode == 'save':
            self.output_frame.configure(text='输出文件')
        else:
            self.output_frame.configure(text='输出文件夹')

        self.output_path_picker = PathPicker(
            self.output_frame,
            mode=self.output_mode,
            file_types=self.output_file_types,
            default_extension=self.output_default_extension,
        )
        self.output_path_picker.pack(side=tk.TOP, fill=tk.X)

    @abstractmethod
    def _set_options_frame(self):
        """创建选项框架"""
        ttk.Label(self.options_frame, text='选项框架').pack(side=tk.TOP)
        pass

    @abstractmethod
    def get_input_files(self) -> tuple[Path, ...]:
        """获取输入文件列表"""
        return (Path(''),)

    @final
    def get_output_path(self) -> Path:
        """获取输出文件路径"""
        return self.output_path_picker.get_path()

    @abstractmethod
    def get_options(self) -> dict:
        """获取选项"""
        return {}

    @final
    def get_pramas(self) -> dict:
        """获取参数"""
        return {
            'input_files': self.get_input_files(),
            'output_path': self.get_output_path(),
            'options': self.get_options(),
        }


if __name__ == '__main__':
    root = tk.Tk()
    frame = BaseFunctionFrame(root, function_id='merge_pdf')
    frame.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
