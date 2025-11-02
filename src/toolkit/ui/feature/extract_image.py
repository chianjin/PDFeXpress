# src/toolkit/ui/feature/extract_image.py
import tkinter as tk
from tkinter import ttk, messagebox

from toolkit.constant import FILE_TYPES_PDF
from toolkit.core.extract_images_worker import extract_images_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_list import FileListView
from toolkit.ui.widget.folder_picker import FolderPicker
from toolkit.ui.widget.misc import TitleFrame, OptionFrame


class ExtractImagesApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.title_frame = TitleFrame(self, text=_("Extract Images"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_list_view = FileListView(
            self,
            title=_("PDF Files to Extract Images From"),
            file_types=FILE_TYPES_PDF,
            sortable=True
        )
        self.file_list_view.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_folder_picker = FolderPicker(self, title=_("Output Folder"))
        self.output_folder_picker.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.option_frame = OptionFrame(self)
        self.option_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

        self.save_in_same_folder_var = tk.BooleanVar(value=False)
        self.save_in_same_folder_checkbox = ttk.Checkbutton(
            self.option_frame,
            text=_("Save in the same folder"),
            variable=self.save_in_same_folder_var,
            command=self._on_save_in_same_folder_changed
        )
        self.save_in_same_folder_checkbox.pack(side="left", padx=10, pady=5)

        ttk.Label(self.option_frame, text=_("Min Width:")).pack(side="left", padx=(10, 5), pady=5)
        self.min_width_var = tk.IntVar(value=100)
        self.min_width_spinbox = ttk.Spinbox(self.option_frame, from_=0, to=10000, increment=1,
                                             textvariable=self.min_width_var, width=5)
        self.min_width_spinbox.pack(side="left", padx=5, pady=5)

        ttk.Label(self.option_frame, text=_("Min Height:")).pack(side="left", padx=(10, 5), pady=5)
        self.min_height_var = tk.IntVar(value=100)
        self.min_height_spinbox = ttk.Spinbox(self.option_frame, from_=0, to=10000, increment=1,
                                              textvariable=self.min_height_var, width=5)
        self.min_height_spinbox.pack(side="left", padx=5, pady=5)

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(bottom_frame, text=_("Extract"), command=self.run_task_from_ui)
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

        self._on_save_in_same_folder_changed()  # Initial state

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
        min_width = self.min_width_var.get()
        min_height = self.min_height_var.get()
        save_in_same_folder = self.save_in_same_folder_var.get()

        if not input_files:
            messagebox.showerror(_("No PDF Files"), _("Please add at least one PDF file."))
            return None

        if not save_in_same_folder and not output_dir:
            messagebox.showerror(_("No Output Folder"), _("Please specify an output folder."))
            return None

        target_function = extract_images_worker
        args_tuple = (input_files, output_dir, min_width, min_height, save_in_same_folder)
        initial_label = _("Extracting images...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
