import tkinter as tk
from tkinter import messagebox, ttk

from toolkit.constant import FILE_TYPES_PDF
from toolkit.core.rotate_pdf_worker import pdf_rotate_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_list import FileListView
from toolkit.ui.widget.folder_picker import FolderPicker
from toolkit.ui.widget.misc import OptionFrame, TitleFrame


class RotatePDFApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.title_frame = TitleFrame(self, text=_('Rotate PDF'))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_list_view = FileListView(
            self, title=_('PDF List'), file_types=FILE_TYPES_PDF, sortable=True
        )
        self.file_list_view.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_folder_picker = FolderPicker(self, title=_('Output Folder'))
        self.output_folder_picker.grid(
            row=2, column=0, sticky='nsew', padx=10, pady=(0, 5)
        )

        self.option_frame = OptionFrame(self, text=_('Options'))
        self.option_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

        self.save_to_same_folder_var = tk.BooleanVar(value=False)
        self.save_to_same_folder_checkbox = ttk.Checkbutton(
            self.option_frame,
            text=_('Save in the same folder'),
            variable=self.save_to_same_folder_var,
            command=self._on_save_to_same_folder_changed,
        )
        self.save_to_same_folder_checkbox.pack(side='left', padx=10, pady=5)

        ttk.Label(self.option_frame, text=_('Rotation Angle:')).pack(
            side='left', padx=(10, 5), pady=5
        )
        self.rotation_angle_var = tk.IntVar(value=90)
        ttk.Radiobutton(
            self.option_frame, text='90°', variable=self.rotation_angle_var, value=90
        ).pack(side='left', padx=5, pady=5)
        ttk.Radiobutton(
            self.option_frame, text='180°', variable=self.rotation_angle_var, value=180
        ).pack(side='left', padx=5, pady=5)
        ttk.Radiobutton(
            self.option_frame, text='270°', variable=self.rotation_angle_var, value=270
        ).pack(side='left', padx=5, pady=5)

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_('Ready'), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(
            bottom_frame, text=_('Rotate'), command=self.run_task_from_ui
        )
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

        self._on_save_to_same_folder_changed()

    def _on_save_to_same_folder_changed(self):
        if self.save_to_same_folder_var.get():
            self.output_folder_picker.set_state('disabled')
        else:
            self.output_folder_picker.set_state('normal')

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        input_files = [str(p) for p in self.file_list_view.get()]
        output_dir = self.output_folder_picker.get()
        rotation_angle = self.rotation_angle_var.get()
        save_to_same_folder = self.save_to_same_folder_var.get()

        if not input_files:
            messagebox.showerror(
                _('Invalid Input'), _('Please add at least one PDF file.')
            )
            return None

        if not save_to_same_folder and not output_dir:
            messagebox.showerror(
                _('Invalid Output'), _('Please specify an output folder.')
            )
            return None

        target_function = pdf_rotate_worker
        args_tuple = (input_files, output_dir, rotation_angle, save_to_same_folder)
        initial_label = _('Rotating PDF...')

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
