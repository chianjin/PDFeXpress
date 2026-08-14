import tkinter as tk
from abc import ABC, abstractmethod
from pathlib import Path
from tkinter import ttk

from util.helpers import get_feature_info
from util.i18n import gettext_text as _
from widget import HeaderFrame


class BaseFeatureFrame(ttk.Frame, ABC):
    def __init__(self, master, feature_id='', **kw):
        super().__init__(master, padding=5, **kw)

        self._feature_id = feature_id
        self._title, self._executive_text = get_feature_info(self._feature_id)

        HeaderFrame(self, feature_id=self._feature_id, title=self._title).pack(
            side=tk.TOP, fill=tk.X, padx=10
        )

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
    def _setup_input_frame(self): ...

    @abstractmethod
    def _setup_output_frame(self): ...

    @abstractmethod
    def _setup_options_frame(self): ...

    @abstractmethod
    def _setup_execute_frame(self): ...

    @abstractmethod
    def get_input_paths(self) -> list[Path]: ...

    @abstractmethod
    def get_output_path(self) -> Path: ...

    @abstractmethod
    def get_options(self) -> dict: ...

    @abstractmethod
    def _execute_handler(self):
        """执行处理器，返回 feature_id 和 params"""
        ...

    @abstractmethod
    def _validate_input_files(self): ...
