from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.file_list_view import FileListView
from ui.functions.base_function_frame import BaseFunctionFrame


class PdfToImagesFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='pdf_to_images', output_mode='folder')
        self._setup_auto_output()

    def _set_input_frame(self):
        self.file_list_view = FileListView(
            self.input_frame,
            sortable=False,
            allow_duplicates=False,
        )
        self.file_list_view.pack(fill=tk.BOTH, expand=True)

    def _setup_auto_output(self):
        first_file_var = self.file_list_view.get_first_file_var()

        def update_output(*_args):
            if not self.output_path_picker.is_auto_output_enabled():
                return

            first_file = first_file_var.get()
            if first_file:
                from pathlib import Path

                path = Path(first_file)
                folder_name = path.stem
                parent_dir = path.parent
                auto_path = parent_dir / folder_name
                self.output_path_picker.set(auto_path, is_auto=True)
            else:
                self.output_path_picker.set('', is_auto=True)

        first_file_var.trace_add('write', update_output)

    def _set_options_frame(self):
        self._dpi = tk.IntVar(value=300)
        self._format = tk.StringVar(value='png')
        self._transparent = tk.BooleanVar(value=True)
        self._quality = tk.IntVar(value=85)

        options_frame = ttk.Frame(self.options_frame)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(options_frame, text='DPI:').pack(side=tk.LEFT)
        ttk.Entry(
            options_frame,
            textvariable=self._dpi,
            width=6,
        ).pack(side=tk.LEFT, padx=(5, 15))

        ttk.Label(options_frame, text='格式').pack(side=tk.LEFT)
        ttk.Radiobutton(
            options_frame,
            text='PNG',
            value='png',
            variable=self._format,
            command=self._update_format_options,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            options_frame,
            text='JPEG',
            value='jpeg',
            variable=self._format,
            command=self._update_format_options,
        ).pack(side=tk.LEFT, padx=(5, 15))

        self.transparent_cb = ttk.Checkbutton(
            options_frame,
            text='透明背景',
            variable=self._transparent,
        )
        self.transparent_cb.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(options_frame, text='质量:').pack(side=tk.LEFT)
        self.quality_entry = ttk.Entry(
            options_frame,
            textvariable=self._quality,
            width=6,
        )
        self.quality_entry.pack(side=tk.LEFT, padx=(5, 0))

        self._format.trace_add('write', self._update_format_options)
        self._update_format_options()

    def _update_format_options(self, *_args):
        if self._format.get() == 'png':
            self.transparent_cb.configure(state=tk.NORMAL)
            self.quality_entry.configure(state=tk.DISABLED)
        else:
            self.transparent_cb.configure(state=tk.DISABLED)
            self.quality_entry.configure(state=tk.NORMAL)

    def get_input_files(self) -> list[Path]:
        return self.file_list_view.get_files()

    def get_options(self) -> dict:
        return {
            'dpi': self._dpi.get(),
            'format': self._format.get(),
            'transparent': self._transparent.get(),
            'quality': self._quality.get(),
        }
