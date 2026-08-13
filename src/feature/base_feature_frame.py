import tkinter as tk
from abc import ABC, abstractmethod
from pathlib import Path
from tkinter import ttk
from typing import Literal, final

from widget import HeaderFrame, PathPicker
from util.file_types import FILE_TYPES
from util.i18n import gettext_text as _
from util.helpers import get_feature_info


class BaseFeatureFrame(ttk.Frame, ABC):
    def __init__(
        self,
        master,
        feature_id='',
        **kw
    ):
        super().__init__(master, padding=5, **kw)

        self._feature_id = feature_id
        self._title, self._executive_text = get_feature_info(self._feature_id)

        HeaderFrame(
            self, feature_id=self._feature_id, title=self._title
        ).pack(side=tk.TOP, fill=tk.X, padx=10)

        self.input_frame = ttk.LabelFrame(self, text=_('Input PDF'), padding=5)
        self.input_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, pady=(5, 0))

        self.output_frame = ttk.LabelFrame(self, text=_('Output PDF'), padding=5)
        self.output_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self.options_frame = ttk.LabelFrame(self, text=_('Options'), padding=5)
        self.options_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self.execute_frame = ttk.LabelFrame(self, text=_('Execute'), padding=5)
        self.execute_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self._setup_input_frame()
        self._setup_output_frame()
        self._setup_options_frame()
        self._setup_execute_frame()

    @abstractmethod
    def _setup_input_frame(self):
        ttk.Label(self.input_frame, text='Input File Frame').pack()
        pass

    @abstractmethod
    def _setup_output_frame(self):
        ttk.Label(self.output_frame, text='Output Frame').pack()
        pass

    @abstractmethod
    def _setup_options_frame(self):
        ttk.Label(self.options_frame, text='Options Frame').pack()
        pass

    @abstractmethod
    def _setup_execute_frame(self):
        ttk.Label(self.execute_frame, text='Execute Frame').pack()
        pass

    @abstractmethod
    def get_input_pathes(self) -> list[Path]:
        return [Path('')]

    @abstractmethod
    def get_output_path(self) -> Path:
        return Path('')

    @abstractmethod
    def get_options(self) -> dict:
        return {}

    @abstractmethod
    def _execute_handler(self):
        """执行处理器，返回 feature_id 和 params"""
        params = {
            'inputs': self.get_input_pathes(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            print(params)

    @abstractmethod
    def _validate_input_files(self):
        return True


if __name__ == '__main__':
    root = tk.Tk()
    frame = BaseFeatureFrame(root, feature_id='merge_pdf')
    frame.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
