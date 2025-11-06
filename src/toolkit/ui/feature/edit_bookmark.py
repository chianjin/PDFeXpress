# toolkit/ui/feature/edit_bookmark.py

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List

from toolkit.constant import FILE_TYPES_CSV, FILE_TYPES_PDF
from toolkit.core.edit_bookmark_worker import (
    export_to_csv,
    get_outlines,
    import_from_csv,
    set_outlines,
)
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
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # Input PDF
        self.input_file_picker = FilePicker(
            self, title=_("PDF File"), mode="open", file_types=FILE_TYPES_PDF
        )
        self.input_file_picker.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.input_file_picker.file_path_var.trace_add("write", self.load_bookmarks)
        self.input_file_picker.file_path_var.trace_add(
            "write", self._on_input_pdf_changed
        )

        # Bookmark List
        list_frame = ttk.Labelframe(self, text=_("Bookmark"))
        list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.toc_tree = ttk.Treeview(
            list_frame, columns=("level", "page", "title"), show="headings"
        )
        self.toc_tree.heading("level", text=_("Level"))
        self.toc_tree.heading("page", text=_("Page"))
        self.toc_tree.heading("title", text=_("Title"))
        self.toc_tree.column("level", width=50, anchor="center", stretch=False)
        self.toc_tree.column("page", width=60, anchor="center", stretch=False)
        self.toc_tree.column("title", width=100)  # Set a minwidth for the title
        self.toc_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.toc_tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.toc_tree.configure(yscrollcommand=vsb.set)
        self.toc_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Action Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=0, column=2, sticky="ns", padx=5, pady=5)

        ttk.Button(button_frame, text=_("Reload"), command=self.load_bookmarks).pack(
            fill="x", pady=2
        )
        ttk.Separator(button_frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Button(
            button_frame, text=_("Import"), command=self.import_toc_from_csv
        ).pack(fill="x", pady=2)
        ttk.Button(button_frame, text=_("Export"), command=self.export_toc_to_csv).pack(
            fill="x", pady=2
        )
        ttk.Separator(button_frame, orient="horizontal").pack(fill="x", pady=10)
        self.move_up_button = ttk.Button(
            button_frame, text=_("Move Up"), command=self.move_up
        )
        self.move_up_button.pack(fill="x", pady=2)
        self.move_down_button = ttk.Button(
            button_frame, text=_("Move Down"), command=self.move_down
        )
        self.move_down_button.pack(fill="x", pady=2)
        ttk.Separator(button_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Button(
            button_frame, text=_("Delete"), command=self.delete_selected_bookmark
        ).pack(fill="x", pady=2)
        ttk.Button(
            button_frame, text=_("Delete All"), command=self.delete_all_bookmarks
        ).pack(fill="x", pady=2)

        # Edit Bookmark
        edit_frame = ttk.Labelframe(self, text=_("Entry"))
        edit_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        edit_frame.columnconfigure(5, weight=1)

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
        self.title_entry.grid(row=0, column=5, sticky="ew", padx=5, pady=5)
        edit_frame.columnconfigure(5, weight=1)

        self.edit_button = ttk.Button(
            edit_frame, text=_("Edit"), command=self.edit_bookmark
        )
        self.edit_button.grid(row=0, column=6, padx=5, pady=5)

        ttk.Button(edit_frame, text=_("Add"), command=self.add_bookmark).grid(
            row=0, column=7, padx=5, pady=5
        )

        # Output
        self.output_file_picker = FilePicker(
            self, title=_("Output PDF"), mode="save", file_types=FILE_TYPES_PDF
        )
        self.output_file_picker.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        # Start Button
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=5, column=0, sticky="e", padx=15, pady=10)
        self.start_button = ttk.Button(
            bottom_frame, text=_("Save"), command=self.apply_changes
        )
        self.start_button.pack()

        self.edit_button.config(state="disabled")
        self.move_up_button.config(state="disabled")
        self.move_down_button.config(state="disabled")

    def _on_input_pdf_changed(self, *args):
        pdf_path_str = self.input_file_picker.get()
        if pdf_path_str:
            pdf_path = Path(pdf_path_str)
            new_stem = f"{pdf_path.stem}_{_('Bookmark')}"
            output_file_path = pdf_path.with_name(f"{new_stem}{pdf_path.suffix}")
            self.output_file_picker.set(str(output_file_path))
        else:
            self.output_file_picker.set("")

    def load_bookmarks(self, *args):
        pdf_path = self.input_file_picker.get()
        if not pdf_path:
            return
        try:
            toc = get_outlines(pdf_path)
            self.update_treeview(toc)
        except Exception as e:
            messagebox.showerror(_("Error"), _("Failed to load: {}").format(e))

    def update_treeview(self, toc: List):
        self.toc_tree.delete(*self.toc_tree.get_children())
        for i, item in enumerate(toc):
            level, page, title = item
            self.toc_tree.insert("", "end", values=(level, page, title))

    def get_toc_from_treeview(self) -> List:
        toc = []
        for iid in self.toc_tree.get_children():
            values = self.toc_tree.item(iid, "values")
            level, page, title = values
            toc.append([int(level), int(page), str(title)])
        return toc

    def on_tree_select(self, event):
        selected_items = self.toc_tree.selection()
        if not selected_items:
            self.selected_item_id = None
            self.edit_button.config(state="disabled")
            self.move_up_button.config(state="disabled")
            self.move_down_button.config(state="disabled")
            return

        self.selected_item_id = selected_items[0]
        values = self.toc_tree.item(self.selected_item_id, "values")
        level, page, title = values
        self.level_var.set(level)
        self.page_var.set(page)
        self.title_var.set(title)

        self.edit_button.config(state="normal")
        self.move_up_button.config(state="normal")
        self.move_down_button.config(state="normal")

    def edit_bookmark(self):
        if not self.selected_item_id or not self.toc_tree.exists(self.selected_item_id):
            messagebox.showerror(_("Invalid Input"), _("No entry selected to edit."))
            return

        try:
            level = int(self.level_var.get())
            page = int(self.page_var.get())
            title = self.title_var.get()
        except ValueError:
            messagebox.showerror(
                _("Invalid Input"), _("Level and Page must be numbers.")
            )
            return

        self.toc_tree.item(self.selected_item_id, values=(level, page, title))
        self.sort_treeview()

    def add_bookmark(self):
        try:
            level = int(self.level_var.get())
            page = int(self.page_var.get())
            title = self.title_var.get()
        except ValueError:
            messagebox.showerror(
                _("Invalid Input"), _("Level and Page must be numbers.")
            )
            return

        if not title:
            messagebox.showerror(_("Invalid Input"), _("Title cannot be empty."))
            return

        self.toc_tree.insert("", "end", values=(level, page, title))
        self.sort_treeview()
        self.level_var.set("")
        self.page_var.set("")
        self.title_var.set("")

    def sort_treeview(self):
        items = [
            (self.toc_tree.set(k, "page"), k) for k in self.toc_tree.get_children("")
        ]
        items.sort(key=lambda t: int(t[0]))
        for index, (val, k) in enumerate(items):
            self.toc_tree.move(k, "", index)

    def move_up(self):
        if not self.selected_item_id:
            return
        self.toc_tree.move(
            self.selected_item_id,
            self.toc_tree.parent(self.selected_item_id),
            self.toc_tree.index(self.selected_item_id) - 1,
        )

    def move_down(self):
        if not self.selected_item_id:
            return
        self.toc_tree.move(
            self.selected_item_id,
            self.toc_tree.parent(self.selected_item_id),
            self.toc_tree.index(self.selected_item_id) + 1,
        )

    def delete_selected_bookmark(self):
        selected_items = self.toc_tree.selection()
        if not selected_items:
            messagebox.showinfo(
                _("Invalid Input"), _("Please select a bookmark to delete.")
            )
            return
        self.toc_tree.delete(*selected_items)

    def delete_all_bookmarks(self):
        if messagebox.askyesno(
            _("Confirm Action"), _("Are you sure you want to delete all bookmarks?")
        ):
            self.toc_tree.delete(*self.toc_tree.get_children())

    def import_toc_from_csv(self):
        path = filedialog.askopenfilename(filetypes=FILE_TYPES_CSV)
        if not path:
            return
        try:
            toc = import_from_csv(path)
            self.update_treeview(toc)
        except Exception as e:
            messagebox.showerror(_("Error"), _("Import failed: {}").format(e))

    def export_toc_to_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=FILE_TYPES_CSV
        )
        if not path:
            return
        try:
            toc = self.get_toc_from_treeview()
            export_to_csv(toc, path)
            messagebox.showinfo(_("Success"), _("Export successful: {}").format(path))
        except Exception as e:
            messagebox.showerror(_("Error"), _("Export failed: {}").format(e))

    def apply_changes(self):
        input_path = self.input_file_picker.get()
        output_path = self.output_file_picker.get()

        if not input_path or not output_path:
            messagebox.showerror(
                _("Invalid Input"), _("Please specify input and output files.")
            )
            return

        try:
            toc = self.get_toc_from_treeview()
            set_outlines(input_path, toc, output_path)
            messagebox.showinfo(
                _("Success"), _("Save successful: {}").format(output_path)
            )
        except Exception as e:
            messagebox.showerror(_("Error"), _("Save failed: {}").format(e))
