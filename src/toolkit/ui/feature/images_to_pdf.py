# src/toolkit/ui/feature/images_to_pdf.py
from tkinter import ttk, messagebox

from toolkit.constant import FILE_TYPES_IMAGES, FILE_TYPES_PDF
from toolkit.core.image_to_pdf_worker import image_to_pdf_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_list import FileListView
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.misc import TitleFrame


class ImagesToPDFApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.output_pdf_path = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.title_frame = TitleFrame(self, text=_("Images to PDF"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.file_list_view = FileListView(
            self,
            title=_("Image Files to Convert"),
            file_types=FILE_TYPES_IMAGES,
            sortable=True,
            on_change_callback=self._on_file_list_changed
        )
        self.file_list_view.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 5))

        self.output_file_picker = FilePicker(
            self,
            title=_("Output PDF File"),
            mode="save",
            file_types=FILE_TYPES_PDF,

        )
        self.output_file_picker.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            bottom_frame,
            text=_("Ready"),
            anchor='w',
        )
        self.status_label.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        self.start_button = ttk.Button(
            bottom_frame,
            text=_("Convert"),
            command=self.run_task_from_ui
        )
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

    def _on_file_list_changed(self):
        files = self.file_list_view.get()
        if files:
            first_file_path = files[0]
            containing_folder = first_file_path.parent
            output_dir = containing_folder.parent
            new_filename = output_dir / f"{containing_folder.name}.pdf"
            self.output_file_picker.set(str(new_filename))
        else:
            self.output_file_picker.clear()

    # Implementation of Mixin contract
    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        image_files = [str(p) for p in self.file_list_view.get()]
        output_pdf_path = self.output_file_picker.get()

        if not image_files:
            messagebox.showerror(_("Input Image Not Enough."), _("Please add at least one image file."))
            return None

        if not output_pdf_path:
            messagebox.showerror(_("No Output PDF Specified."), _("Please specify an output PDF file."))
            return None

        target_function = image_to_pdf_worker
        args_tuple = (image_files, output_pdf_path)
        initial_label = _("Converting images...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)


if __name__ == "__main__":
    import tkinterdnd2

    root = tkinterdnd2.Tk()
    root.geometry("1024x600")
    app = ImagesToPDFApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()