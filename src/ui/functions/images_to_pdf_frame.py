from contextlib import suppress
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class ImagesToPdfFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='images_to_pdf', output_mode='file')

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=True,
            allow_duplicates=True,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _set_options_frame(self):
        self._size_mode = tk.StringVar(value='original')
        self._page_size = tk.StringVar(value='A4')
        self._custom_width = tk.IntVar(value=210)
        self._custom_height = tk.IntVar(value=297)
        self._orientation = tk.StringVar(value='portrait')
        self._fit_mode = tk.StringVar(value='fit')

        size_mode_frame = ttk.Frame(self.options_frame)
        size_mode_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(size_mode_frame, text='尺寸模式').pack(side=tk.LEFT)
        ttk.Radiobutton(
            size_mode_frame,
            text='原始尺寸',
            value='original',
            variable=self._size_mode,
            command=self._update_size_options_state,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            size_mode_frame,
            text='统一尺寸',
            value='uniform',
            variable=self._size_mode,
            command=self._update_size_options_state,
        ).pack(side=tk.LEFT, padx=(5, 0))

        uniform_frame = ttk.Frame(self.options_frame)
        uniform_frame.pack(side=tk.TOP, fill=tk.X)

        page_size_frame = ttk.Frame(uniform_frame)
        page_size_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(page_size_frame, text='页面尺寸').pack(side=tk.LEFT)
        self.page_size_combo = ttk.Combobox(
            page_size_frame,
            textvariable=self._page_size,
            values=['A3', 'A4', 'A5', 'Letter', 'Legal', '自定义'],
            state='readonly',
            width=10,
        )
        self.page_size_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.page_size_combo.bind('<<ComboboxSelected>>', self._on_page_size_changed)

        ttk.Label(page_size_frame, text='宽:').pack(side=tk.LEFT)
        self.width_entry = ttk.Entry(
            page_size_frame,
            textvariable=self._custom_width,
            width=8,
        )
        self.width_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(page_size_frame, text='mm').pack(side=tk.LEFT, padx=(2, 10))

        ttk.Label(page_size_frame, text='高:').pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(
            page_size_frame,
            textvariable=self._custom_height,
            width=8,
        )
        self.height_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(page_size_frame, text='mm').pack(side=tk.LEFT, padx=(2, 0))

        orientation_frame = ttk.Frame(uniform_frame)
        orientation_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(orientation_frame, text='版式').pack(side=tk.LEFT)
        ttk.Radiobutton(
            orientation_frame,
            text='竖版',
            value='portrait',
            variable=self._orientation,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            orientation_frame,
            text='横版',
            value='landscape',
            variable=self._orientation,
        ).pack(side=tk.LEFT, padx=(5, 0))

        fit_mode_frame = ttk.Frame(uniform_frame)
        fit_mode_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(fit_mode_frame, text='适应模式').pack(side=tk.LEFT)
        ttk.Radiobutton(
            fit_mode_frame,
            text='适应',
            value='fit',
            variable=self._fit_mode,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            fit_mode_frame,
            text='填充',
            value='fill',
            variable=self._fit_mode,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            fit_mode_frame,
            text='拉伸',
            value='stretch',
            variable=self._fit_mode,
        ).pack(side=tk.LEFT, padx=(5, 0))

        self._size_mode.trace_add('write', self._update_size_options_state)
        self._update_size_options_state()

    def _on_page_size_changed(self, *_args):
        if self._page_size.get() == '自定义':
            self.width_entry.configure(state=tk.NORMAL)
            self.height_entry.configure(state=tk.NORMAL)
        else:
            self.width_entry.configure(state=tk.DISABLED)
            self.height_entry.configure(state=tk.DISABLED)

    def _update_size_options_state(self, *_args):
        uniform_frame = self.options_frame.winfo_children()[1]
        if self._size_mode.get() == 'uniform':
            for widget in uniform_frame.winfo_children():
                for child in widget.winfo_children():
                    with suppress(tk.TclError):
                        child.configure(state=tk.NORMAL)
            self._on_page_size_changed()
        else:
            for widget in uniform_frame.winfo_children():
                for child in widget.winfo_children():
                    with suppress(tk.TclError):
                        child.configure(state=tk.DISABLED)

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_files()

    def get_options(self) -> dict:
        return {
            'size_mode': self._size_mode.get(),
            'page_size': self._page_size.get(),
            'width': self._custom_width.get(),
            'height': self._custom_height.get(),
            'orientation': self._orientation.get(),
            'fit_mode': self._fit_mode.get(),
        }
