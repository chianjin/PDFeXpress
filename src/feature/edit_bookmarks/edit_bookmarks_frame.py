import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror, showinfo

import pymupdf

from feature.base_feature_frame import BaseFeatureFrame
from util.file_types import FILE_TYPES
from util.i18n import gettext_text as _
from util.helpers import enable_pdf_drop


class EditBookmarksFrame(BaseFeatureFrame):
    def __init__(self, master, **kw):
        super().__init__(master, feature_id='edit_bookmarks', **kw)

    def _setup_input_frame(self):
        self.input_frame.configure(text=_('Input PDF'))
        self._input_path = tk.StringVar()
        row = ttk.Frame(self.input_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self._input_path).pack(
            side='left', fill='x', expand=True
        )
        ttk.Button(row, text=_('Browser'), command=self._browse_input).pack(
            side='left', padx=(5, 0)
        )
        # Fixed single-input: collapse to natural height.
        self.input_frame.pack_configure(expand=False, fill='x')
        enable_pdf_drop(self.input_frame, self._input_path)

    def _setup_output_frame(self):
        self.output_frame.configure(text=_('Output PDF'))
        self.output_path = tk.StringVar()
        row = ttk.Frame(self.output_frame)
        row.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        ttk.Entry(row, textvariable=self.output_path).pack(
            side='left', fill='x', expand=True
        )
        ttk.Button(row, text=_('Browser'), command=self._set_output).pack(
            side='left', padx=(5, 0)
        )
        self.output_frame.pack_configure(expand=False, fill='x')

    def _setup_options_frame(self):
        self.options_frame.configure(text=_('Bookmarks'))

        area = ttk.Frame(self.options_frame)
        area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=2, pady=2)
        area.columnconfigure(0, weight=1)
        area.rowconfigure(0, weight=1)

        # Treeview: level / page / title (order is immutable).
        self.tree = ttk.Treeview(
            area,
            columns=('level', 'page', 'title'),
            show='headings',
            selectmode='browse',
            height=14,
        )
        self.tree.heading('level', text=_('Level'), anchor='w')
        self.tree.heading('page', text=_('Page'), anchor='w')
        self.tree.heading('title', text=_('Title'), anchor='w')
        self.tree.column('level', width=60, anchor='w')
        self.tree.column('page', width=60, anchor='w')
        self.tree.column('title', width=300, anchor='w')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        scrollbar = ttk.Scrollbar(area, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Right-side action buttons.
        button_col = ttk.Frame(area)
        button_col.grid(row=0, column=2, sticky='ns', padx=(5, 0))
        for text, command in (
            (_('Reload'), self._reload),
            (_('Import'), self._import_csv),
            (_('Export'), self._export_csv),
            (_('Move Up'), lambda: self._move(-1)),
            (_('Move Down'), lambda: self._move(1)),
            (_('Delete'), self._delete_selected),
            (_('Delete All'), self._delete_all),
        ):
            ttk.Button(button_col, text=text, command=command).pack(
                fill='x', pady=(0, 4)
            )

        # Bottom item form: level / page / title + Edit / Add.
        self._level_var = tk.StringVar()
        self._page_var = tk.StringVar()
        self._title_var = tk.StringVar()
        form = ttk.Frame(area)
        form.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(6, 0))
        ttk.Label(form, text=_('Level')).pack(side='left', padx=(0, 3))
        ttk.Entry(form, textvariable=self._level_var, width=6).pack(
            side='left', padx=(0, 8)
        )
        ttk.Label(form, text=_('Page')).pack(side='left', padx=(0, 3))
        ttk.Entry(form, textvariable=self._page_var, width=6).pack(
            side='left', padx=(0, 8)
        )
        ttk.Label(form, text=_('Title')).pack(side='left', padx=(0, 3))
        ttk.Entry(form, textvariable=self._title_var).pack(
            side='left', fill='x', expand=True, padx=(0, 8)
        )
        ttk.Button(form, text=_('Edit'), command=self._edit_selected).pack(
            side='left', padx=(2, 2)
        )
        ttk.Button(form, text=_('Add'), command=self._add_bookmark).pack(side='left')

    def _setup_execute_frame(self):
        ttk.Button(
            self.execute_frame,
            text=_('Save'),
            command=self._execute_handler,
        ).pack(side='right', padx=(5, 0))

    # ---- file browsing ----
    def _browse_input(self):
        init = self._initial_dir(self._input_path.get())
        path = askopenfilename(filetypes=FILE_TYPES['PDF'], initialdir=init)
        if path:
            src = Path(path)
            self._input_path.set(src)
            if not self.output_path.get():
                self.output_path.set(src.with_suffix(f'.{_("TOC")}.pdf'))

    def _set_output(self):
        init = self._initial_dir(self.output_path.get())
        default = ''
        if self._input_path.get():
            default = Path(self._input_path.get()).with_suffix(f'.{_("TOC")}.pdf').name
        path = asksaveasfilename(
            filetypes=FILE_TYPES['PDF'],
            initialdir=init,
            initialfile=default,
        )
        if path:
            self.output_path.set(Path(path))

    @staticmethod
    def _initial_dir(current: str) -> Path | str:
        if current:
            return Path(current).parent
        return ''

    # ---- tree <-> form ----
    def _on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], 'values')
        if len(vals) >= 3:
            self._level_var.set(str(vals[0]))
            self._page_var.set(str(vals[1]))
            self._title_var.set(str(vals[2]))

    def _read_form(self):
        """Validate the form; return (level, page, title) or None on error."""
        level_s = self._level_var.get().strip()
        page_s = self._page_var.get().strip()
        title = self._title_var.get()
        if not title.strip():
            showerror(title=_('Error'), message=_('Bookmark title must not be empty.'))
            return None
        try:
            level = int(level_s)
            page = int(page_s)
        except ValueError:
            showerror(title=_('Error'), message=_('Level and Page must be integers.'))
            return None
        if level < 1:
            showerror(title=_('Error'), message=_('Level must be >= 1.'))
            return None
        return level, page, title

    def _add_bookmark(self):
        form = self._read_form()
        if form is None:
            return
        level, page, title = form
        self.tree.insert('', tk.END, values=(level, page, title))
        self._title_var.set('')

    def _edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            showerror(title=_('Error'), message=_('Select a bookmark to edit.'))
            return
        form = self._read_form()
        if form is None:
            return
        level, page, title = form
        self.tree.item(sel[0], values=(level, page, title))

    def _move(self, delta: int):
        """Move selected bookmark up (-1) / down (+1); single-select only."""
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if (delta < 0 and idx == 0) or (delta > 0 and idx == self.tree.count() - 1):
            return
        self.tree.move(sel[0], '', idx + delta)

    def _delete_selected(self):
        for item in self.tree.selection()[::-1]:
            self.tree.delete(item)

    def _delete_all(self):
        for item in self.tree.get_children()[::-1]:
            self.tree.delete(item)

    def _reload(self):
        src = self._input_path.get().strip()
        if not src or not Path(src).is_file():
            showerror(title=_('Error'), message=_('Input PDF must be set.'))
            return
        with pymupdf.open(src) as doc:
            toc = doc.get_toc()  # [[level, title, page], ...], page 1-based
        self._delete_all()
        for level, title, page in toc:
            self.tree.insert('', tk.END, values=(level, page, title))

    def _import_csv(self):
        path = askopenfilename(
            filetypes=[(_('CSV files'), '*.csv'), (_('All files'), '*.*')]
        )
        if not path:
            return
        from feature.edit_bookmarks.edit_bookmarks_worker import read_csv_bookmarks

        try:
            rows = read_csv_bookmarks(Path(path))
        except Exception as exc:
            showerror(title=_('Error'), message=_('Failed to import: {}').format(exc))
            return
        self._delete_all()
        for level, page, title in rows:
            self.tree.insert('', tk.END, values=(level, page, title))

    def _export_csv(self):
        path = asksaveasfilename(
            defaultextension='.csv',
            filetypes=[(_('CSV files'), '*.csv'), (_('All files'), '*.*')],
        )
        if not path:
            return
        rows = [list(self.tree.item(it, 'values')) for it in self.tree.get_children()]
        from feature.edit_bookmarks.edit_bookmarks_worker import write_csv_bookmarks

        try:
            write_csv_bookmarks(Path(path), rows)
        except Exception as exc:
            showerror(title=_('Error'), message=_('Failed to export: {}').format(exc))
            return
        showinfo(title=_('Done'), message=_('Bookmarks exported'))

    # ---- abstract overrides ----
    def get_input_paths(self):
        return [Path(self._input_path.get())]

    def get_output_path(self):
        return Path(self.output_path.get())

    def get_options(self) -> dict:
        return {}

    def _validate_execute_params(self) -> bool:
        """Validate the input PDF and the bookmark table before writing the TOC.

        Returns True when everything is usable; otherwise shows an error
        dialog and returns False. Runs synchronously (single-shot operation,
        no multiprocessing).
        """
        src = self._input_path.get().strip()
        if not src:
            showerror(title=_('Error'), message=_('Input PDF must be set.'))
            return False
        if not Path(src).is_file():
            showerror(title=_('Error'), message=_('Input PDF does not exist.'))
            return False
        if not self.output_path.get().strip():
            showerror(title=_('Error'), message=_('Output PDF must be set.'))
            return False

        try:
            with pymupdf.open(src) as doc:
                page_count = doc.page_count
        except Exception as exc:
            showerror(title=_('Error'), message=_('Cannot open input PDF: {}').format(exc))
            return False

        items = self.tree.get_children()
        if not items:
            showerror(title=_('Error'), message=_('No bookmarks to write.'))
            return False

        for item in items:
            vals = self.tree.item(item, 'values')
            try:
                level = int(vals[0])
                page = int(vals[1])
            except (ValueError, IndexError):
                showerror(
                    title=_('Error'),
                    message=_('Level and Page must be integers.'),
                )
                return False
            if level < 1:
                showerror(title=_('Error'), message=_('Level must be >= 1.'))
                return False
            if page < 1 or page > page_count:
                showerror(
                    title=_('Error'),
                    message=_('Page {} out of range (1-{}).').format(page, page_count),
                )
                return False
            title = vals[2] if len(vals) > 2 else ''
            if not title.strip():
                showerror(
                    title=_('Error'), message=_('Bookmark title must not be empty.')
                )
                return False
        return True

    def _execute_handler(self):
        if not self._validate_execute_params():
            return
        src = self._input_path.get().strip()
        out = self.output_path.get().strip()

        toc = []
        for item in self.tree.get_children():
            vals = self.tree.item(item, 'values')
            toc.append([int(vals[0]), vals[2], int(vals[1])])

        from feature.edit_bookmarks.edit_bookmarks_worker import apply_bookmarks

        try:
            apply_bookmarks(src, out, toc)
        except Exception as exc:
            showerror(title=_('Error'), message='{}: {}'.format(type(exc).__name__, exc))
            return
        showinfo(title=_('Done'), message=_('Bookmarks updated'))


if __name__ == '__main__':
    from tkinterdnd2 import TkinterDnD

    root = TkinterDnD.Tk()
    EditBookmarksFrame(root).pack(fill='both', expand=True)
    root.mainloop()
