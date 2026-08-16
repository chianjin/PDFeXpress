import os
import tkinter as tk
from pathlib import Path
import pymupdf
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror

from tkinterdnd2 import TkinterDnD

from config import EXECUTIVE_PATH
from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.page_number_rule import build_page_number_map
from util.i18n import gettext_text as _
from util.helpers import enable_pdf_drop
from widget.help_window import HelpWindow

FONT_FAMILIES = ['Courier', 'Times', 'Helvetica']
FONT_STYLES = ['Regular', 'Bold', 'Italic', 'Bold Italic']


class AddPageNumbersFrame(BaseFeatureFrame):
    """Add page numbers to a single PDF.

    A single input PDF and a single output PDF. The numbering follows the rule
    syntax documented in ``asset/page_number_syntax_guide-zh_CN.txt``; pages not
    covered by the rule carry no number.
    """

    def __init__(self, master, **kw):
        super().__init__(master, feature_id='add_page_numbers', **kw)
        self._page_map: dict[int, str] = {}
        self._total_pages = 0

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))

        self.input_path = tk.StringVar()
        row = ttk.Frame(self.input_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self.input_path).pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(row, text=_('Browser'), command=self._browse).pack(
            side='left', padx=(5, 0)
        )

        # Single fixed-height input row: collapse the frame instead of letting
        # it stretch (base class defaults expand=True, which suits list views).
        self.input_frame.pack_configure(expand=False, fill='x')
        enable_pdf_drop(self.input_frame, self.input_path)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output PDF'))
        self.output_path = tk.StringVar()
        ttk.Entry(self.output_frame, textvariable=self.output_path).pack(
            side='left', expand=True, fill='x'
        )
        ttk.Button(
            self.output_frame, text=_('Browser'), command=self._set_output_path
        ).pack(side='left', padx=(5, 0))

    def _setup_options_frame(self):
        # Page number rule + help button.
        rule_row = ttk.Frame(self.options_frame)
        ttk.Label(rule_row, text=_('Page Number Rule')).pack(side='left')
        self._rule = tk.StringVar(value='1-')
        ttk.Entry(rule_row, textvariable=self._rule, width=30).pack(
            side='left', padx=(5, 0)
        )
        self.help_icon = tk.PhotoImage(file=EXECUTIVE_PATH / 'asset/icon/help.png')
        ttk.Button(
            rule_row, image=self.help_icon, style='Toolbutton', command=self._open_help
        ).pack(side='left')
        ttk.Label(
            rule_row,
            text=_('Default: continuous numbering from 1. Click Help for details.'),
        ).pack(side='left', padx=(5, 0))
        rule_row.pack(side=tk.TOP, fill='x')

        # Font family / style / size.
        font_row = ttk.Frame(self.options_frame)
        ttk.Label(font_row, text=_('Font')).pack(side='left')
        self._font_family = tk.StringVar(value='Times')
        ttk.Combobox(
            font_row,
            textvariable=self._font_family,
            values=FONT_FAMILIES,
            state='readonly',
            width=10,
        ).pack(side='left', padx=(5, 0))
        self._font_bold = tk.BooleanVar(value=False)
        ttk.Checkbutton(font_row, text=_('Bold'), variable=self._font_bold).pack(
            side='left', padx=(5, 0)
        )
        ttk.Label(font_row, text=_('Size')).pack(side='left', padx=(10, 0))
        self._font_size = tk.IntVar(value=11)
        ttk.Spinbox(
            font_row,
            textvariable=self._font_size,
            from_=1,
            to=200,
            width=6,
            justify='center',
        ).pack(side='left', padx=(5, 0))
        font_row.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        # Position: vertical (header/footer) | horizontal (left/center/right) |
        # mirror (outside/inside).
        self._vertical = tk.StringVar(value='footer')
        self._horizontal = tk.StringVar(value='center')
        pos_row = ttk.Frame(self.options_frame)
        ttk.Label(pos_row, text=_('Position')).pack(side='left', padx=(0, 5))
        ttk.Radiobutton(
            pos_row,
            text=_('Header'),
            variable=self._vertical,
            value='header',
            command=self._refresh_margins,
        ).pack(side='left')
        ttk.Radiobutton(
            pos_row,
            text=_('Footer'),
            variable=self._vertical,
            value='footer',
            command=self._refresh_margins,
        ).pack(side='left', padx=(5, 0))
        ttk.Label(pos_row, text='|').pack(side='left', padx=(8, 8))
        ttk.Radiobutton(
            pos_row,
            text=_('Left'),
            variable=self._horizontal,
            value='left',
            command=self._refresh_margins,
        ).pack(side='left')
        ttk.Radiobutton(
            pos_row,
            text=_('Center'),
            variable=self._horizontal,
            value='center',
            command=self._refresh_margins,
        ).pack(side='left', padx=(5, 0))
        ttk.Radiobutton(
            pos_row,
            text=_('Right'),
            variable=self._horizontal,
            value='right',
            command=self._refresh_margins,
        ).pack(side='left', padx=(5, 0))
        ttk.Label(pos_row, text='|').pack(side='left', padx=(8, 8))
        ttk.Radiobutton(
            pos_row,
            text=_('Outside'),
            variable=self._horizontal,
            value='outside',
            command=self._refresh_margins,
        ).pack(side='left')
        ttk.Radiobutton(
            pos_row,
            text=_('Inside'),
            variable=self._horizontal,
            value='inside',
            command=self._refresh_margins,
        ).pack(side='left', padx=(5, 0))
        pos_row.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        # Dynamic margins (rebuilt whenever the position selection changes).
        self._top_margin = tk.DoubleVar(value=1.5)
        self._bottom_margin = tk.DoubleVar(value=1.5)
        self._left_margin = tk.DoubleVar(value=2.0)
        self._right_margin = tk.DoubleVar(value=2.0)
        self._mirror_margin = tk.DoubleVar(value=2.0)
        self._margin_frame = ttk.Frame(self.options_frame)
        self._margin_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        self._refresh_margins()

    def _refresh_margins(self):
        for child in self._margin_frame.winfo_children():
            child.destroy()
        vertical = self._vertical.get()
        horizontal = self._horizontal.get()
        if vertical == 'header':
            self._add_margin_field(_('Top Margin'), self._top_margin)
        else:
            self._add_margin_field(_('Bottom Margin'), self._bottom_margin)
        if horizontal == 'left':
            self._add_margin_field(_('Left Margin'), self._left_margin)
        elif horizontal == 'right':
            self._add_margin_field(_('Right Margin'), self._right_margin)
        elif horizontal in ('outside', 'inside'):
            self._add_margin_field(_('Margin'), self._mirror_margin)
        # center -> no horizontal margin field

    def _add_margin_field(self, label, var):
        field = ttk.Frame(self._margin_frame)
        ttk.Label(field, text=label).pack(side='left', padx=(0, 5))
        ttk.Spinbox(
            field,
            textvariable=var,
            from_=0,
            to=20,
            increment=0.1,
            width=8,
            justify='center',
        ).pack(side='left')
        ttk.Label(field, text='cm').pack(side='left', padx=(2, 0))
        field.pack(side='left', padx=(0, 10))

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_(self._executive_text),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    def _open_help(self):
        posix_lang = os.environ.get('LANG', 'en_US.UTF-8')
        language = posix_lang.split('.')[0]
        guide_path = EXECUTIVE_PATH / f'asset/page_number_syntax_guide-{language}.txt'
        if not guide_path.exists():
            guide_path = EXECUTIVE_PATH / 'asset/page_number_syntax_guide-en_US.txt'
        with open(guide_path, encoding='UTF-8') as f:
            help_content = f.readlines()
        title = help_content[0].strip()
        content = ''.join(help_content[1:])
        HelpWindow(self, title=title, content=content).focus()

    def _browse(self):
        init = self._initial_dir(self.input_path.get())
        path = askopenfilename(filetypes=FILE_TYPES['PDF'], initialdir=init)
        if path:
            self.input_path.set(Path(path))

    def _initial_dir(self, current: str) -> Path | str:
        if current:
            return Path(current).parent
        return ''

    def _set_output_path(self):
        init_folder = ''
        init_file = ''
        current_input_path = self._get_current_input_path()
        if current_input_path:
            init_folder = current_input_path.parent
            init_file = current_input_path.with_suffix(f'.{_("PageNum")}.pdf').name
        output_path = asksaveasfilename(
            filetypes=FILE_TYPES['PDF'],
            defaultextension='pdf',
            initialdir=init_folder,
            initialfile=init_file,
            confirmoverwrite=True,
        )
        if output_path:
            self.output_path.set(Path(output_path))

    def _get_current_input_path(self):
        current = self.output_path.get()
        if current:
            return Path(current)
        if self.input_path.get():
            return Path(self.input_path.get())
        return None

    def get_input_paths(self):
        return [Path(self.input_path.get())] if self.input_path.get() else []

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        # Variables are typed (IntVar/DoubleVar/BooleanVar/StringVar), so
        # .get() already returns the correct type. The worker trusts this
        # dict as-is; validation happened in _validate_execute_params().
        return {
            'page_map': self._page_map,
            'total_pages': self._total_pages,
            'font_family': self._font_family.get(),
            'font_bold': self._font_bold.get(),
            'font_size': self._font_size.get(),
            'vertical': self._vertical.get(),
            'horizontal': self._horizontal.get(),
            'top_margin_cm': self._top_margin.get(),
            'bottom_margin_cm': self._bottom_margin.get(),
            'left_margin_cm': self._left_margin.get(),
            'right_margin_cm': self._right_margin.get(),
            'mirror_margin_cm': self._mirror_margin.get(),
        }

    def _execute_handler(self):
        params = {
            'inputs': self.get_input_paths(),
            'output': self.get_output_path(),
            'options': self.get_options(),
        }
        if self._validate_execute_params():
            from feature.add_page_numbers.add_page_numbers_worker import (
                run_add_page_numbers_with_progress,
            )

            run_add_page_numbers_with_progress(self.winfo_toplevel(), params)

    def _validate_execute_params(self):
        if not self.input_path.get():
            showerror(title=_('Error'), message=_('Input PDF cannot be empty.'))
            return False
        if not self.output_path.get():
            showerror(title=_('Error'), message=_('Output PDF cannot be empty.'))
            return False
        if not self._rule.get().strip():
            showerror(title=_('Error'), message=_('Page number rule must be set.'))
            return False
        if self._font_size.get() < 1:
            showerror(title=_('Error'), message=_('Font size must be at least 1.'))
            return False
        for var in (
            self._top_margin,
            self._bottom_margin,
            self._left_margin,
            self._right_margin,
            self._mirror_margin,
        ):
            if var.get() < 0:
                showerror(title=_('Error'), message=_('Margin must be greater than 0.'))
                return False
        try:
            with pymupdf.open(self.input_path.get()) as doc:
                total = doc.page_count
            self._page_map = build_page_number_map(self._rule.get(), total)
            self._total_pages = total
        except Exception as exc:
            showerror(title=_('Error'), message=f'{type(exc).__name__}: {exc}')
            return False
        return True


if __name__ == '__main__':
    root = TkinterDnD.Tk()
    AddPageNumbersFrame(root).pack(fill='both', expand=True)
    root.mainloop()
