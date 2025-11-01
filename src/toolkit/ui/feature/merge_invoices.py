# src/toolkit/ui/feature/merge_invoices.py
from tkinter import ttk, messagebox

from toolkit.constant import FILE_TYPES_PDF
from toolkit.core.merge_invoices_worker import merge_invoices_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_list import FileListView
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.misc import TitleFrame


class MergeInvoicesApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Set weight to the file list

        self.title_frame = TitleFrame(self, text=_("Merge Invoices"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.invoice_list_view = FileListView(
            self,
            title=_("Invoice PDF Files"),
            file_types=FILE_TYPES_PDF,
            sortable=True
        )
        self.invoice_list_view.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_file_picker = FilePicker(self, title=_("Output PDF File"), mode="save", file_types=FILE_TYPES_PDF)
        self.output_file_picker.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(bottom_frame, text=_("Merge"), command=self.run_task_from_ui)
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        invoice_pdf_paths = [str(p) for p in self.invoice_list_view.get()]
        output_pdf_path = self.output_file_picker.get()

        if not invoice_pdf_paths:
            messagebox.showerror(_("No Invoice PDFs"), _("Please add at least one invoice PDF file."))
            return None

        if not output_pdf_path:
            messagebox.showerror(_("No Output File Specified"), _("Please specify an output file."))
            return None

        target_function = merge_invoices_worker
        args_tuple = (invoice_pdf_paths, output_pdf_path)
        initial_label = _("Merging invoices...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
