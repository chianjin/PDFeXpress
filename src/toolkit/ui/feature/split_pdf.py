# src/toolkit/ui/feature/split_pdf.py
import tkinter as tk
from tkinter import ttk, messagebox

from toolkit.constant import FILE_TYPES_PDF
from toolkit.core.split_pdf_worker import split_pdf_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.folder_picker import FolderPicker
from toolkit.ui.widget.misc import TitleFrame, OptionFrame


class SplitPDFApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)

        self.title_frame = TitleFrame(self, text=_("Split PDF"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_picker = FilePicker(self, title=_("Input PDF"), file_types=FILE_TYPES_PDF)
        self.file_picker.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_folder_picker = FolderPicker(self, title=_("Output Folder"))
        self.output_folder_picker.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.option_frame = OptionFrame(self, text=_("Options"))
        self.option_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

        self.split_mode_var = tk.StringVar(value="single_page")
        self.split_mode_var.trace_add("write", self._on_split_mode_changed)

        modes = [
            ("Single Page", "single_page"),
            ("By Pages", "fixed_pages"),
            ("By Copies", "fixed_files"),
            ("Custom Ranges", "custom_ranges"),
        ]

        radio_frame = ttk.Frame(self.option_frame)
        radio_frame.pack(fill='x', padx=10, pady=5)
        for text, mode in modes:
            ttk.Radiobutton(
                radio_frame,
                text=_(text),
                variable=self.split_mode_var,
                value=mode
            ).pack(side='left', padx=5, pady=5)

        self.split_value_label = ttk.Label(radio_frame, text=_("Value:"))
        self.split_value_label.pack(side='left', padx=(10, 5), pady=5)

        self.split_value_var = tk.StringVar()
        self.split_value_entry = ttk.Entry(radio_frame, textvariable=self.split_value_var)
        self.split_value_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)

        # Fixed description label
        self.fixed_description_label = ttk.Label(
            self.option_frame,
            text=_("e.g., By Pages: 5  |  By Range: 1,3,5-10"),
            justify=tk.LEFT
        )
        self.fixed_description_label.pack(fill='x', padx=10, pady=(0, 5))

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(bottom_frame, text=_("Split"), command=self.run_task_from_ui)
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

        self._on_split_mode_changed()  # Initial state

    def _on_split_mode_changed(self, *args):
        mode = self.split_mode_var.get()
        if mode == "single_page":
            self.split_value_entry.config(state="disabled")
        else:
            self.split_value_entry.config(state="normal")

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        pdf_path = self.file_picker.get()
        output_dir = self.output_folder_picker.get()
        split_mode = self.split_mode_var.get()
        split_value = self.split_value_var.get()

        if not pdf_path:
            messagebox.showerror(_("Invalid Input"), _("Please select an input PDF."))
            return None

        if not output_dir:
            messagebox.showerror(_("Invalid Input"), _("Please specify an output path."))
            return None

        if split_mode in ["fixed_pages", "fixed_files", "custom_ranges"] and not split_value:
            messagebox.showerror(_("Invalid Input"), _("Please specify a value for the split mode."))
            return None

        target_function = split_pdf_worker
        args_tuple = (pdf_path, output_dir, split_mode, split_value)
        initial_label = _("Splitting PDF...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
