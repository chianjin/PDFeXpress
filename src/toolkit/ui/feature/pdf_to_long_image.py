import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from toolkit.constant import FILE_TYPES_JPEG, FILE_TYPES_PDF
from toolkit.core.pdf_to_long_image_worker import pdf_to_long_image_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.misc import OptionFrame, TitleFrame


class PDFToLongImageApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.columnconfigure(0, weight=1)

        self.title_frame = TitleFrame(self, text=_('PDF to Long Image'))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_picker = FilePicker(
            self, title=_('PDF File'), file_types=FILE_TYPES_PDF
        )
        self.file_picker.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))
        self.file_picker.file_path_var.trace_add('write', self._on_input_pdf_changed)

        self.output_file_picker = FilePicker(
            self, title=_('JPEG File'), mode='save', file_types=FILE_TYPES_JPEG
        )
        self.output_file_picker.grid(
            row=2, column=0, sticky='nsew', padx=10, pady=(0, 5)
        )

        self.option_frame = OptionFrame(self, text=_('Options'))
        self.option_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 5))

        ttk.Label(self.option_frame, text=_('DPI:')).pack(
            side='left', padx=(10, 0), pady=5
        )
        self.dpi_var = tk.IntVar(value=150)
        self.dpi_spinbox = ttk.Spinbox(
            self.option_frame,
            from_=72,
            to=600,
            increment=1,
            textvariable=self.dpi_var,
            width=5,
        )
        self.dpi_spinbox.pack(side='left', padx=5, pady=5)

        ttk.Label(self.option_frame, text=_('Image Quality:')).pack(
            side='left', padx=(10, 0), pady=5
        )
        self.quality_var = tk.IntVar(value=75)
        self.quality_spinbox = ttk.Spinbox(
            self.option_frame,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.quality_var,
            width=5,
        )
        self.quality_spinbox.pack(side='left', padx=5, pady=5)

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_('Ready'), anchor='w')
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(
            bottom_frame, text=_('Convert'), command=self.run_task_from_ui
        )
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

    def _on_input_pdf_changed(self, *args):
        pdf_path_str = self.file_picker.get()
        if pdf_path_str:
            pdf_path = Path(pdf_path_str)
            file_name_without_ext = pdf_path.stem
            output_filename = f'{file_name_without_ext}.jpg'
            output_file_path = pdf_path.parent / output_filename
            self.output_file_picker.set(str(output_file_path))
        else:
            self.output_file_picker.set('')

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        pdf_path = self.file_picker.get()
        output_image_path = self.output_file_picker.get()
        dpi_value = self.dpi_var.get()
        quality_value = self.quality_var.get()

        if not pdf_path:
            messagebox.showerror(_('Invalid Input'), _('Please select an input PDF.'))
            return None

        if not output_image_path:
            messagebox.showerror(
                _('Invalid Input'), _('Please specify an output JPEG file.')
            )
            return None

        target_function = pdf_to_long_image_worker
        args_tuple = (pdf_path, output_image_path, dpi_value, quality_value)
        initial_label = _('Converting to long image...')

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)
