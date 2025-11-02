# src/toolkit/ui/feature/interleave_pdf.py
import tkinter as tk
from tkinter import ttk, messagebox

from toolkit.constant import FILE_TYPES_PDF
from toolkit.core.interleave_pdfs_worker import interleave_pdfs_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.misc import TitleFrame, OptionFrame


class InterleavePDFApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)

        self.title_frame = TitleFrame(self, text=_("Interleave PDF"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.pdf_a_picker = FilePicker(self, title=_("PDF File A"), file_types=FILE_TYPES_PDF)
        self.pdf_a_picker.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.pdf_b_picker = FilePicker(self, title=_("PDF File B"), file_types=FILE_TYPES_PDF)
        self.pdf_b_picker.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_file_picker = FilePicker(self, title=_("Output PDF File"), mode="save", file_types=FILE_TYPES_PDF)
        self.output_file_picker.grid(row=3, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.option_frame = OptionFrame(self)
        self.option_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 5))

        self.reverse_b_var = tk.BooleanVar(value=True)
        self.reverse_b_checkbox = ttk.Checkbutton(
            self.option_frame,
            text=_("Reverse second PDF"),
            variable=self.reverse_b_var
        )
        self.reverse_b_checkbox.pack(side="left", padx=10, pady=5)

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=5, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(bottom_frame, text=_("Interleave"), command=self.run_task_from_ui)
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        pdf_path_a = self.pdf_a_picker.get()
        pdf_path_b = self.pdf_b_picker.get()
        output_pdf_path = self.output_file_picker.get()
        reverse_b = self.reverse_b_var.get()

        if not pdf_path_a or not pdf_path_b:
            messagebox.showerror(_("Missing PDF Files"), _("Please select both PDF files."))
            return None

        if not output_pdf_path:
            messagebox.showerror(_("No Output File"), _("Please specify an output file."))
            return None

        target_function = interleave_pdfs_worker
        args_tuple = (pdf_path_a, pdf_path_b, output_pdf_path, reverse_b)
        initial_label = _("Interleaving PDFs...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
