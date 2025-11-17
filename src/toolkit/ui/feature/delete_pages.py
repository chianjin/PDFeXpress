"""UI module for deleting pages from PDF files."""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

from toolkit.constant import FILE_TYPES_PDF, HELP_ICON
from toolkit.core.delete_pages_worker import delete_pages_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.folder_picker import FolderPicker
from toolkit.ui.widget.help_window import HelpWindow
from toolkit.ui.widget.misc import OptionFrame, TitleFrame
from toolkit.util.help_contents import PAGE_RANGE_SELECTION


class DeletePagesApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master: tk.Tk, **kwargs: Any) -> None:
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)
        self.help_window = None

        self.columnconfigure(0, weight=1)

        self.title_frame = TitleFrame(self, text=_('Delete Pages'))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_picker = FilePicker(
            self, title=_('PDF File'), file_types=FILE_TYPES_PDF
        )
        self.file_picker.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))
        self.file_picker.file_path_var.trace_add('write', self._on_input_changed)

        self.output_folder_picker = FolderPicker(self, title=_('Output Folder'))
        self.output_folder_picker.grid(
            row=2, column=0, sticky='nsew', padx=10, pady=(0, 5)
        )

        self.option_frame = OptionFrame(self, text=_('Options'))
        self.option_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

        ttk.Label(self.option_frame, text=_('Pages to Delete:')).pack(
            side='left', padx=(10, 5), pady=5
        )

        self.pages_to_delete_var = tk.StringVar()
        self.pages_to_delete_var.trace_add('write', self._on_input_changed)

        self.pages_to_delete_entry = ttk.Entry(
            self.option_frame, textvariable=self.pages_to_delete_var
        )
        self.pages_to_delete_entry.pack(
            side='left', fill='x', expand=True, padx=10, pady=5
        )

        self.help_icon = tk.PhotoImage(file=HELP_ICON)
        ttk.Button(
            self.option_frame,
            image=self.help_icon,
            style='Toolbutton',
            command=self._show_syntax_help,
            cursor='hand2',
        ).pack(side='left', padx=5, pady=0, anchor='center')

        ttk.Label(self.option_frame, text=PAGE_RANGE_SELECTION['brief']).pack(
            side='left', padx=(5, 20)
        )

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_('Ready'), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(
            bottom_frame, text=_('Delete'), command=self.run_task_from_ui
        )
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

        self._on_input_changed()

    def _on_input_changed(self, *args) -> None:
        pdf_path_str = self.file_picker.get()
        if pdf_path_str:
            pdf_path = Path(pdf_path_str)
            file_name_without_ext = pdf_path.stem
            output_folder_name = f'{file_name_without_ext}_{_("Delete")}'
            output_dir = pdf_path.parent / output_folder_name
            self.output_folder_picker.set(str(output_dir))
        else:
            self.output_folder_picker.set('')

    def _show_syntax_help(self, event: tk.Event | None = None) -> None:
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.lift()
            return
        self.help_window = HelpWindow(
            self,
            title=PAGE_RANGE_SELECTION['title'],
            help_text=PAGE_RANGE_SELECTION['content'],
            on_close=self.on_help_window_close,
        )

    def on_help_window_close(self):
        self.help_window = None

    def _get_root_window(self) -> tk.Tk:
        return self.winfo_toplevel()

    def _prepare_task(self) -> tuple[Any, tuple[str, str, str], str] | None:
        pdf_path = self.file_picker.get()
        output_dir = self.output_folder_picker.get()
        pages_to_delete_str = self.pages_to_delete_var.get()

        if not pdf_path:
            messagebox.showerror(
                _('Invalid Input'), _('Please select an input PDF file.')
            )
            return None

        if not output_dir:
            messagebox.showerror(
                _('Invalid Output'), _('Please specify an output folder.')
            )
            return None

        if not pages_to_delete_str:
            messagebox.showerror(
                _('Invalid Page Numbers'), _('Please specify page numbers.')
            )
            return None

        target_function = delete_pages_worker
        args_tuple = (pdf_path, output_dir, pages_to_delete_str)
        initial_label = _('Deleting pages...')

        return target_function, args_tuple, initial_label

    def update_status(self, message: str) -> None:
        self.status_label.config(text=message)
