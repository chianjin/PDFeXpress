# src/toolkit/ui/feature/pdf_to_image.py
import tkinter as tk
from tkinter import ttk, messagebox

from toolkit.constant import FILE_TYPES_PDF
from toolkit.core.pdf_to_image_worker import pdf_to_image_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_list import FileListView
from toolkit.ui.widget.folder_picker import FolderPicker
from toolkit.ui.widget.misc import TitleFrame, OptionFrame


class PDFToImageApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.title_frame = TitleFrame(self, text=_("PDF to Image"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_list_view = FileListView(
            self,
            title=_("PDF Files to Convert"),
            file_types=FILE_TYPES_PDF,
            sortable=True
        )
        self.file_list_view.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_folder_picker = FolderPicker(self, title=_("Output Folder"))
        self.output_folder_picker.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.option_frame = OptionFrame(self)
        self.option_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

        # Save in same folder
        self.save_in_same_folder_var = tk.BooleanVar(value=False)
        self.save_in_same_folder_checkbox = ttk.Checkbutton(
            self.option_frame,
            text=_("Save In Same Folder"),
            variable=self.save_in_same_folder_var,
            command=self._on_save_in_same_folder_changed
        )
        self.save_in_same_folder_checkbox.pack(side="left", padx=10, pady=5)

        # DPI
        ttk.Label(self.option_frame, text=_("DPI:")).pack(side="left", padx=(10, 5), pady=5)
        self.dpi_var = tk.IntVar(value=300)
        self.dpi_spinbox = ttk.Spinbox(self.option_frame, from_=72, to=600, increment=1, textvariable=self.dpi_var,
                                       width=5)
        self.dpi_spinbox.pack(side="left", padx=5, pady=5)

        # Format
        ttk.Label(self.option_frame, text=_("Format:")).pack(side="left", padx=(10, 5), pady=5)
        self.format_var = tk.StringVar(value="jpg")
        self.format_var.trace_add("write", self._on_format_changed)
        ttk.Radiobutton(self.option_frame, text="PNG", variable=self.format_var, value="png").pack(side="left", padx=5,
                                                                                                   pady=5)
        ttk.Radiobutton(self.option_frame, text="JPG", variable=self.format_var, value="jpg").pack(side="left", padx=5,
                                                                                                   pady=5)

        # JPEG Quality
        self.jpeg_quality_label = ttk.Label(self.option_frame, text=_("JPEG Quality:"))
        self.jpeg_quality_var = tk.IntVar(value=85)
        self.jpeg_quality_spinbox = ttk.Spinbox(self.option_frame, from_=1, to=100, increment=1,
                                                textvariable=self.jpeg_quality_var, width=5)

        # PNG Transparency
        self.transparent_background_var = tk.BooleanVar(value=False)
        self.transparent_background_checkbox = ttk.Checkbutton(
            self.option_frame,
            text=_("Transparent Background"),
            variable=self.transparent_background_var
        )

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(bottom_frame, text=_("Convert"), command=self.run_task_from_ui)
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

        self._on_format_changed()  # Initial state
        self._on_save_in_same_folder_changed()  # Initial state

    def _on_format_changed(self, *args):
        if self.format_var.get() == "jpg":
            self.jpeg_quality_label.pack(side="left", padx=(10, 5), pady=5)
            self.jpeg_quality_spinbox.pack(side="left", padx=5, pady=5)
            self.transparent_background_checkbox.pack_forget()
        else:  # png
            self.jpeg_quality_label.pack_forget()
            self.jpeg_quality_spinbox.pack_forget()
            self.transparent_background_checkbox.pack(side="left", padx=10, pady=5)

    def _on_save_in_same_folder_changed(self):
        if self.save_in_same_folder_var.get():
            self.output_folder_picker.set_state("disabled")
        else:
            self.output_folder_picker.set_state("normal")

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        input_files = [str(p) for p in self.file_list_view.get()]
        output_dir = self.output_folder_picker.get()
        dpi_value = self.dpi_var.get()
        image_format = self.format_var.get()
        jpeg_quality = self.jpeg_quality_var.get()
        transparent_background = self.transparent_background_var.get()
        save_in_same_folder = self.save_in_same_folder_var.get()

        if not input_files:
            messagebox.showerror(_("No Input Files"), _("Please add at least one PDF file to convert."))
            return None

        if not save_in_same_folder and not output_dir:
            messagebox.showerror(_("No Output Folder Specified"), _("Please specify an output folder."))
            return None

        target_function = pdf_to_image_worker
        args_tuple = (input_files, output_dir, dpi_value, image_format, jpeg_quality, transparent_background,
                      save_in_same_folder)
        initial_label = _("Converting PDFs to images...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
