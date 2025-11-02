# src/toolkit/ui/feature/delete_page.py
import tkinter as tk
from tkinter import ttk, messagebox

from toolkit.constant import FILE_TYPES_PDF
from toolkit.core.delete_pages_worker import delete_pages_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.misc import TitleFrame, OptionFrame


class DeletePageApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)

        self.title_frame = TitleFrame(self, text=_("Delete Page"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_picker = FilePicker(self, title=_("PDF File to Modify"), file_types=FILE_TYPES_PDF)
        self.file_picker.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_file_picker = FilePicker(self, title=_("Output PDF File"), mode="save", file_types=FILE_TYPES_PDF)
        self.output_file_picker.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.option_frame = OptionFrame(self, text=_("Pages to Delete"))
        self.option_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

        self.pages_to_delete_var = tk.StringVar()
        self.pages_to_delete_entry = ttk.Entry(self.option_frame, textvariable=self.pages_to_delete_var)
        self.pages_to_delete_entry.pack(fill="x", expand=True, padx=10, pady=5)
        ttk.Label(self.option_frame, text=_("e.g., 1-3, 5, 7-9")).pack(anchor="w", padx=10, pady=(0, 5))

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(bottom_frame, text=_("Delete"), command=self.run_task_from_ui)
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        pdf_path = self.file_picker.get()
        output_path = self.output_file_picker.get()
        pages_to_delete_str = self.pages_to_delete_var.get()

        if not pdf_path:
            messagebox.showerror(_("No Input File"), _("Please select a PDF file."))
            return None

        if not output_path:
            messagebox.showerror(_("No Output File Specified"), _("Please specify an output file."))
            return None

        if not pages_to_delete_str:
            messagebox.showerror(_("No Pages Specified"), _("Please specify the pages to delete."))
            return None

        target_function = delete_pages_worker
        args_tuple = (pdf_path, output_path, pages_to_delete_str)
        initial_label = _("Deleting pages...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
