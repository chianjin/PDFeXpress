# src/toolkit/ui/feature/image_to_pdf.py
import tkinter as tk
from tkinter import ttk, messagebox
import os

from toolkit.i18n import gettext_text as _
from toolkit.constant import FILE_TYPES_IMAGES, FILE_TYPES_PDF
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget._file_list import FileList
from toolkit.ui.widget._file_picker import FilePicker
from toolkit.ui.widget._misc import Title
from toolkit.core.image_to_pdf_worker import image_to_pdf_worker

class ImageToPdfApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, padding="20", **kwargs)
        TaskRunnerMixin.__init__(self)

        self.output_pdf_path = None

        # --- GUI --- 
        # 应用标题
        self.title_frame = Title(self, text=_("Image to PDF Converter"))
        self.title_frame.pack(pady=(0, 10))

        # 文件列表
        self.file_list = FileList(
            self,
            title=_("1. Select Image Files (Drag & Drop Supported)"),
            file_types=FILE_TYPES_IMAGES,

        )
        self.file_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 输出 PDF 文件选择
        self.output_file_picker = FilePicker(
            self,
            title=_("2. Select Output PDF File"),
            mode="save",
            file_types=FILE_TYPES_PDF,

        )
        self.output_file_picker.pack(fill=tk.X, pady=(0, 10))

        # 执行按钮
        self.start_button = ttk.Button(
            self,
            text=_("3. Convert Images to PDF"),
            command=self.run_task_from_ui
        )
        self.start_button.pack(pady=(10, 0), ipadx=10, ipady=10, fill=tk.X)

    # --- 实现 Mixin "契约" ---
    def _get_root_window(self):
        return self.winfo_toplevel()



    def _prepare_task(self):
        image_files = [str(p) for p in self.file_list.get()]
        output_pdf_path = self.output_file_picker.get()

        if not image_files:
            messagebox.showerror(_("Input Incomplete"), _("Please add at least one image file."))
            return None
        
        if not output_pdf_path:
            messagebox.showerror(_("Input Incomplete"), _("Please select an output PDF file."))
            return None
        
        if os.path.exists(output_pdf_path):
            if not messagebox.askyesno(
                _("Overwrite File?"),
                _("The output file already exists. Do you want to overwrite it?")
            ):
                return None

        target_function = image_to_pdf_worker
        args_tuple = (image_files, output_pdf_path)
        initial_label = _("Converting images...")

        return (target_function, args_tuple, initial_label)


