import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import showerror
from pathlib import Path

from widget import FileListView
from feature.base_feature_frame import BaseFeatureFrame
from util.i18n import gettext_text as _
from util.file_types import FILE_TYPES


class AddWatermarkFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='add_watermark', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('PDF List'))
        self.file_list_view = FileListView(self.input_frame, sortable=False)
        self.file_list_view.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output Folder'))
        self.output_path = tk.StringVar()
        ttk.Entry(self.output_frame, textvariable=self.output_path).pack(
            side='left', fill='x', expand=True
        )
        ttk.Button(
            self.output_frame, text=_('Browser'), command=self._set_output_folder
        ).pack(side='left', padx=(5, 0))

    def _setup_options_frame(self):
        self._mode = tk.StringVar(value='text')

        ttk.Radiobutton(
            self.options_frame, text=_('Text Watermark'),
            variable=self._mode, value='text', command=self._on_mode_change,
        ).pack(side='top', anchor='w')
        ttk.Radiobutton(
            self.options_frame, text=_('Image Watermark'),
            variable=self._mode, value='image', command=self._on_mode_change,
        ).pack(side='top', anchor='w')

        # Text sub-controls (shown when "text" is selected).
        self._text_frame = ttk.Frame(self.options_frame)
        ttk.Label(self._text_frame, text=_('Watermark Text')).pack(
            side='left', padx=(0, 5)
        )
        self._text_entry = tk.StringVar()
        ttk.Entry(self._text_frame, textvariable=self._text_entry, width=30).pack(
            side='left', fill='x', expand=True
        )

        # Image sub-controls (shown when "image" is selected).
        self._image_frame = ttk.Frame(self.options_frame)
        ttk.Label(self._image_frame, text=_('Watermark Image')).pack(
            side='left', padx=(0, 5)
        )
        self._image_path = tk.StringVar()
        ttk.Entry(self._image_frame, textvariable=self._image_path).pack(
            side='left', fill='x', expand=True
        )
        ttk.Button(
            self._image_frame, text=_('Browser'), command=self._browse_image
        ).pack(side='left', padx=(5, 0))

        self._on_mode_change()

    def _on_mode_change(self):
        if self._mode.get() == 'text':
            self._image_frame.pack_forget()
            self._text_frame.pack(side='top', fill='x', pady=(4, 0))
        else:
            self._text_frame.pack_forget()
            self._image_frame.pack(side='top', fill='x', pady=(4, 0))

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame, text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _browse_image(self):
        current = self._image_path.get()
        init = str(Path(current).parent) if current else (self._get_initial_dir() or '')
        path = askopenfilename(filetypes=FILE_TYPES['IMAGES'], initialdir=init)
        if path:
            self._image_path.set(str(Path(path)))

    def get_input_pathes(self):
        return self.file_list_view.get_file_paths()

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {
            'mode': self._mode.get(),
            'text': self._text_entry.get(),
            'image_path': self._image_path.get(),
        }

    def _set_output_folder(self):
        init_dir = self._get_initial_dir()
        folder = askdirectory(initialdir=init_dir)
        if folder:
            self.output_path.set(str(Path(folder)))

    def _get_initial_dir(self):
        current = self.output_path.get()
        if current:
            return Path(current)
        inputs = self.get_input_pathes()
        if inputs:
            return inputs[0].parent
        return None

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_pathes(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_input_files():
            from feature.add_watermark.add_watermark_worker import (
                run_add_watermark_with_progress,
            )
            run_add_watermark_with_progress(self.winfo_toplevel(), params)

    def _validate_input_files(self):
        if len(self.get_input_pathes()) < 1:
            showerror(
                title=_('Error'),
                message=_('Input must have at least 1 PDF file.'),
            )
            return False
        if not self.output_path.get():
            showerror(
                title=_('Error'),
                message=_('Output folder must be set.'),
            )
            return False
        if self._mode.get() == 'text':
            if not self._text_entry.get().strip():
                showerror(
                    title=_('Error'),
                    message=_('Watermark text must be set.'),
                )
                return False
        else:
            image_path = self._image_path.get().strip()
            if not image_path:
                showerror(
                    title=_('Error'),
                    message=_('Watermark image must be set.'),
                )
                return False
            if not Path(image_path).is_file():
                showerror(
                    title=_('Error'),
                    message=_('Watermark image does not exist.'),
                )
                return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    AddWatermarkFrame(root).pack(fill='both', expand=True)
    root.mainloop()
