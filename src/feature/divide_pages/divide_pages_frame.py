import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror

from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.helpers import enable_pdf_drop
from util.i18n import gettext_text as _


class DividePagesFrame(BaseFeatureFrame):
    """Split every page of a single PDF into N equal strips.

    Direction (vertical/horizontal) and part count are configurable;
    a landscape A3 divided vertically into 2 gives two portrait A4 pages.
    Mirrors the single-input/output layout of ``decrypt_pdf``; output
    defaults to ``{stem}.{_('Divide')}.pdf`` next to the input.
    """

    def __init__(self, master, **kw):
        super().__init__(master, feature_id='divide_pages', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))

        self.input_path = tk.StringVar()
        row = ttk.Frame(self.input_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self.input_path, state='readonly').pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(row, text=_('Browser'), command=self._set_input_path).pack(side='left', padx=(5, 0))

        # Single fixed-height input row (same collapse as decrypt_pdf).
        self.input_frame.pack_configure(expand=False, fill='x')
        enable_pdf_drop(self.input_frame, self.input_path)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output PDF'))
        self.output_path = tk.StringVar()
        ttk.Entry(self.output_frame, textvariable=self.output_path, state='readonly').pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(self.output_frame, text=_('Browser'), command=self._set_output_path).pack(
            side='left', padx=(5, 0)
        )

    def _setup_options_frame(self):
        direction_row = ttk.Frame(self.options_frame)
        direction_row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Label(direction_row, text=_('Direction')).pack(side='left', padx=(0, 5))
        self._direction = tk.StringVar(value='vertical')
        for value, text in (
            ('vertical', _('Vertical (left/right)')),
            ('horizontal', _('Horizontal (top/bottom)')),
        ):
            ttk.Radiobutton(direction_row, text=text, value=value, variable=self._direction).pack(
                side='left', padx=(0, 10)
            )

        parts_row = ttk.Frame(self.options_frame)
        parts_row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Label(parts_row, text=_('Parts')).pack(side='left', padx=(0, 5))
        self._parts = tk.IntVar(value=2)
        ttk.Spinbox(parts_row, from_=2, to=10, textvariable=self._parts, width=4).pack(side='left')

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _set_input_path(self):
        path = askopenfilename(filetypes=FILE_TYPES['PDF'])
        if path:
            path = Path(path)
            self.input_path.set(path)
            self.output_path.set(path.with_suffix(f'.{_("Divide")}.pdf'))

    def _set_output_path(self):
        output_path = self.output_path.get()
        init_folder = Path(output_path).parent if output_path else ''
        init_file = Path(output_path).name if output_path else ''
        output_path = asksaveasfilename(
            filetypes=FILE_TYPES['PDF'],
            defaultextension='pdf',
            initialdir=init_folder,
            initialfile=init_file,
            confirmoverwrite=True,
        )
        if output_path:
            self.output_path.set(Path(output_path))

    def get_input_paths(self):
        return [Path(self.input_path.get())] if self.input_path.get() else []

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {
            'direction': self._direction.get(),
            'parts': int(self._parts.get()),
        }

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if not self._validate_execute_params():
            return
        from feature.divide_pages.divide_pages_worker import (
            run_divide_pages_with_progress,
        )

        run_divide_pages_with_progress(self.winfo_toplevel(), params)

    def _validate_execute_params(self):
        if not self.input_path.get():
            showerror(
                title=_('Error'),
                message=_('Input PDF must be set.'),
            )
            return False
        if not self.output_path.get():
            showerror(
                title=_('Error'),
                message=_('Output path must be set.'),
            )
            return False
        if int(self._parts.get()) < 2:
            showerror(
                title=_('Error'),
                message=_('Divide into at least 2 parts.'),
            )
            return False
        return True


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    DividePagesFrame(root).pack(fill='both', expand=True)
    root.mainloop()
