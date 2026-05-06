from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Literal, final

from core.function_list import FUNCTION_LIST
from ui.components import ExecuteFrame, HeaderFrame, PathPicker
from utils.auto_output_helpers import (
    setup_auto_output_file_to_file,
    setup_auto_output_file_to_folder,
    setup_auto_output_list_to_file,
    setup_auto_output_list_to_folder,
)
from utils.file_types import FILE_TYPES


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
        self._setup_auto_output()

    def _setup_ui(self):
        HeaderFrame(self, function_id=self.function_id).pack(side=tk.TOP, fill=tk.X, padx=10)

        self.input_frame = ttk.LabelFrame(self, text='PDF 文件', padding=5)
        self.input_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, pady=(5, 0))

        self.output_frame = ttk.LabelFrame(self, text='输出 PDF', padding=5)
        self.output_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self.options_frame = ttk.LabelFrame(self, text='选项', padding=5)
        self.options_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self.execute_frame = ExecuteFrame(self, FUNCTION_LIST[self.function_id].execute_text)
        self.execute_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

    @abstractmethod
    def _set_input_frame(self):
        ttk.Label(self.input_frame, text='输入文件框架').pack(side=tk.TOP)
        pass

    @final
    def _set_output_frame(self):

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

    @final
    def _setup_auto_output(self):
        """
        设置auto_output联动机制。
        子类可通过覆盖 _get_auto_output_strategy 方法来自定义策略。
        """
        strategy = self._get_auto_output_strategy()
        if strategy is None:
            return

        strategy(self)

    def _get_auto_output_strategy(self) -> Callable | None:
        """
        返回auto_output策略函数。
        默认根据output_mode和输入组件类型选择策略。
        子类可覆盖此方法以自定义策略。
        """
        if hasattr(self, 'file_list_view'):
            if self.output_mode == 'folder':
                return lambda frame: setup_auto_output_list_to_folder(
                    frame.file_list_view, frame.output_path_picker
                )
            else:
                return lambda frame: setup_auto_output_list_to_file(
                    frame.file_list_view,
                    frame.output_path_picker,
                    frame._generate_output_filename,
                )
        elif hasattr(self, 'input_path_picker'):
            if self.output_mode == 'folder':
                return lambda frame: setup_auto_output_file_to_folder(
                    frame.input_path_picker, frame.output_path_picker
                )
            else:
                return lambda frame: setup_auto_output_file_to_file(
                    frame.input_path_picker, frame.output_path_picker
                )
        return None

    def _generate_output_filename(self, first_file: Path) -> str:
        """
        生成输出文件名（用于多文件->单文件场景）。
        子类应覆盖此方法以提供自定义命名规则。
        """
        return first_file.name

    @abstractmethod
    def _set_options_frame(self):
        ttk.Label(self.options_frame, text='选项框架').pack(side=tk.TOP)
        pass

    @abstractmethod
    def get_input_files(self) -> list[Path]:
        return [Path('')]

    @final
    def get_output_path(self) -> Path:
        return self.output_path_picker.get_path()

    @abstractmethod
    def get_options(self) -> dict:
        return {}

    @final
    def get_pramas(self) -> dict:
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
