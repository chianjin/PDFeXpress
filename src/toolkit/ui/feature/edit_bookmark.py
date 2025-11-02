# src/toolkit/ui/feature/edit_bookmark.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List

import pymupdf

from toolkit.constant import FILE_TYPES_PDF, FILE_TYPES_CSV
from toolkit.core.edit_bookmark_worker import get_bookmarks, set_bookmarks, import_bookmarks_from_csv, \
    export_bookmarks_to_csv
from toolkit.i18n import gettext_text as _
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.misc import TitleFrame


class EditBookmarkApp(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.selected_item_id = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Title
        self.title_frame = TitleFrame(self, text=_("Edit Bookmark"))
        self.title_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # 1. Input PDF
        self.input_file_picker = FilePicker(self, title=_("Source PDF File"), mode="open", file_types=FILE_TYPES_PDF)
        self.input_file_picker.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        self.input_file_picker.file_path_var.trace_add('write', self.load_bookmarks)

        # 2. Bookmark List
        list_frame = ttk.Labelframe(self, text=_("Bookmarks"))
        list_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.toc_tree = ttk.Treeview(list_frame, columns=('level', 'page', 'title'), show='headings')
        self.toc_tree.heading('level', text=_('Level'))
        self.toc_tree.heading('page', text=_('Page'))
        self.toc_tree.heading('title', text=_('Title'))
        self.toc_tree.column('level', width=50, anchor='center')
        self.toc_tree.column('page', width=50, anchor='center')
        self.toc_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.toc_tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.toc_tree.configure(yscrollcommand=vsb.set)
        self.toc_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Action Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=0, column=2, sticky='ns', padx=5, pady=5)


        ttk.Button(button_frame, text=_("Reload"), command=self.load_bookmarks).pack(fill='x', pady=2)
        ttk.Separator(button_frame, orient='horizontal').pack(fill='x', pady=10)


        ttk.Button(button_frame, text=_("Import CSV"), command=self.import_toc_from_csv).pack(fill='x', pady=2)
        ttk.Button(button_frame, text=_("Export CSV"), command=self.export_toc_to_csv).pack(fill='x', pady=2)
        ttk.Separator(button_frame, orient='horizontal').pack(fill='x', pady=10)
        self.move_up_button = ttk.Button(button_frame, text=_("Move Up"), command=self.move_up)
        self.move_up_button.pack(fill='x', pady=2)
        self.move_down_button = ttk.Button(button_frame, text=_("Move Down"), command=self.move_down)
        self.move_down_button.pack(fill='x', pady=2)
        ttk.Separator(button_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Button(button_frame, text=_("Delete"), command=self.delete_selected_bookmark).pack(fill='x', pady=2)
        ttk.Button(button_frame, text=_("Delete All"), command=self.delete_all_bookmarks).pack(fill='x', pady=2)

        # 3. Edit Bookmark
        edit_frame = ttk.Labelframe(self, text=_("Add / Edit Bookmark"))
        edit_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=5)
        edit_frame.columnconfigure(4, weight=1)

        ttk.Label(edit_frame, text=_("Level:")).grid(row=0, column=0, padx=5, pady=5)
        self.level_var = tk.StringVar()
        self.level_entry = ttk.Entry(edit_frame, textvariable=self.level_var, width=5)
        self.level_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_frame, text=_("Page:")).grid(row=0, column=2, padx=5, pady=5)
        self.page_var = tk.StringVar()
        self.page_entry = ttk.Entry(edit_frame, textvariable=self.page_var, width=5)
        self.page_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(edit_frame, text=_("Title:")).grid(row=0, column=4, padx=5, pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(edit_frame, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=5, sticky='ew', padx=5, pady=5)
        edit_frame.columnconfigure(5, weight=1)

        self.edit_button = ttk.Button(edit_frame, text=_("Edit"), command=self.edit_bookmark)
        self.edit_button.grid(row=0, column=6, padx=5, pady=5)

        ttk.Button(edit_frame, text=_("Add"), command=self.add_bookmark).grid(row=0, column=7, padx=5, pady=5)

        # 4. Output
        self.output_file_picker = FilePicker(self, title=_("Output PDF File"), mode="save", file_types=FILE_TYPES_PDF)
        self.output_file_picker.grid(row=4, column=0, sticky='ew', padx=10, pady=5)

        # 5. Start Button
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=5, column=0, sticky='e', padx=15, pady=10)
        self.start_button = ttk.Button(bottom_frame, text=_("Apply"), command=self.apply_changes)
        self.start_button.pack()

        self.edit_button.config(state='disabled')
        self.move_up_button.config(state='disabled')
        self.move_down_button.config(state='disabled')

    def load_bookmarks(self, *args):
        pdf_path = self.input_file_picker.get()
        if not pdf_path:
            return
        try:
            toc = get_bookmarks(pdf_path)
            self.update_treeview(toc)
        except Exception as e:
            messagebox.showerror(_("Error"), _("Failed to load bookmarks: {}").format(e))

    def update_treeview(self, toc: List):
        self.toc_tree.delete(*self.toc_tree.get_children())
        for i, item in enumerate(toc):
            level, title, page = item
            self.toc_tree.insert('', 'end', values=(level, page, title))

    def get_toc_from_treeview(self) -> List:
        toc = []
        for iid in self.toc_tree.get_children():
            values = self.toc_tree.item(iid, 'values')
            level, page, title = values
            toc.append([int(level), str(title), int(page)])
        return toc

    def on_tree_select(self, event):
        selected_items = self.toc_tree.selection()
        if not selected_items:
            self.selected_item_id = None
            self.edit_button.config(state='disabled')
            self.move_up_button.config(state='disabled')
            self.move_down_button.config(state='disabled')
            return

        self.selected_item_id = selected_items[0]
        values = self.toc_tree.item(self.selected_item_id, 'values')
        level, page, title = values
        self.level_var.set(level)
        self.page_var.set(page)
        self.title_var.set(title)

        self.edit_button.config(state='normal')
        self.move_up_button.config(state='normal')
        self.move_down_button.config(state='normal')

    def add_bookmark(self):
        try:
            level = int(self.level_var.get())
            page = int(self.page_var.get())
            title = self.title_var.get()
        except ValueError:
            messagebox.showerror(_("Invalid Input"), _("Level and Page must be integers."))
            return

        if not title:
            messagebox.showerror(_("Invalid Input"), _("Title cannot be empty."))
            return

        self.toc_tree.insert('', 'end', values=(level, page, title))
        self.sort_treeview()

    def edit_bookmark(self):
        if not self.selected_item_id or not self.toc_tree.exists(self.selected_item_id):
            messagebox.showerror(_("Error"), _("No bookmark selected to edit."))
            return

        try:
            level = int(self.level_var.get())
            page = int(self.page_var.get())
            title = self.title_var.get()
        except ValueError:
            messagebox.showerror(_("Invalid Input"), _("Level and Page must be integers."))
            return

        if not title:
            messagebox.showerror(_("Invalid Input"), _("Title cannot be empty."))
            return

        self.toc_tree.item(self.selected_item_id, values=(level, page, title))
        self.sort_treeview()

    def sort_treeview(self):
        items = [(self.toc_tree.set(k, 'page'), k) for k in self.toc_tree.get_children('')]
        items.sort(key=lambda t: int(t[0]))
        for index, (val, k) in enumerate(items):
            self.toc_tree.move(k, '', index)

    def move_up(self):
        if not self.selected_item_id:
            return
        self.toc_tree.move(self.selected_item_id, self.toc_tree.parent(self.selected_item_id), self.toc_tree.index(self.selected_item_id) - 1)

    def move_down(self):
        if not self.selected_item_id:
            return
        self.toc_tree.move(self.selected_item_id, self.toc_tree.parent(self.selected_item_id), self.toc_tree.index(self.selected_item_id) + 1)

    def delete_selected_bookmark(self):
        selected_items = self.toc_tree.selection()
        if not selected_items:
            messagebox.showinfo(_("No Selection"), _("Please select a bookmark to delete."))
            return
        self.toc_tree.delete(selected_items)

    def delete_all_bookmarks(self):
        if messagebox.askyesno(_("Confirm"), _("Are you sure you want to delete all bookmarks?")):
            self.toc_tree.delete(*self.toc_tree.get_children())


    def import_toc_from_csv(self):
        path = filedialog.askopenfilename(filetypes=FILE_TYPES_CSV)
        if not path:
            return
        try:
            toc = import_bookmarks_from_csv(path)
            self.update_treeview(toc)
        except Exception as e:
            messagebox.showerror(_("Error"), _("Failed to import bookmarks from CSV: {}").format(e))


    def export_toc_to_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=FILE_TYPES_CSV)
        if not path:
            return
        try:
            toc = self.get_toc_from_treeview()
            export_bookmarks_to_csv(toc, path)
            messagebox.showinfo(_("Success"), _("Bookmarks successfully exported to {}").format(path))
        except Exception as e:
            messagebox.showerror(_("Error"), _("Failed to export bookmarks to CSV: {}").format(e))

    def apply_changes(self):
        input_path = self.input_file_picker.get()
        output_path = self.output_file_picker.get()

        if not input_path or not output_path:
            messagebox.showerror(_("Missing Information"), _("Please specify both input and output files."))
            return

        try:
            toc = self.get_toc_from_treeview()
            set_bookmarks(input_path, toc, output_path)
            messagebox.showinfo(_("Success"), _("Bookmarks successfully applied to {}").format(output_path))
        except Exception as e:
            messagebox.showerror(_("Error"), _("Failed to apply bookmarks: {}").format(e))

