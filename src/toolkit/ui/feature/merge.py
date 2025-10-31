# src/toolkit/ui/features/merge.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from tkinterdnd2 import DND_FILES

from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.core.merge_pdf_worker import pdf_merge_worker
from toolkit.i18n import gettext_text as _

class MergePdfApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, padding="20", **kwargs)
        TaskRunnerMixin.__init__(self)

        self.input_files = []
        self.output_file = None

        # --- GUI ---
        list_frame = ttk.LabelFrame(self, text=_("1. PDFs to merge (drag files here)"))
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.listbox = tk.Listbox(list_frame, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.on_drop_files)

        self.btn_frame = ttk.Frame(list_frame)
        self.btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self.add_btn = ttk.Button(self.btn_frame, text=_("Add Files"), command=self.add_files_dialog)
        self.add_btn.pack(pady=5)
        self.remove_btn = ttk.Button(self.btn_frame, text=_("Remove Selected"), command=self.remove_file)
        self.remove_btn.pack(pady=5)
        self.clear_btn = ttk.Button(self.btn_frame, text=_("Clear List"), command=self.clear_files)
        self.clear_btn.pack(pady=5)

        out_frame = ttk.Frame(self)
        out_frame.pack(fill=tk.X, pady=5)
        self.out_button = ttk.Button(out_frame, text=_("2. Select Output File"), command=self.select_output)
        self.out_button.pack(side=tk.LEFT)
        self.out_label = ttk.Label(out_frame, text=_("Not selected"))
        self.out_label.pack(side=tk.LEFT, padx=10)

        self.start_button = ttk.Button(self, text=_("3. Start Merging"), command=self.run_task_from_ui)
        self.start_button.pack(pady=10, ipadx=10, ipady=10, fill=tk.X)

    # --- 实现 Mixin "契约" ---
    def _get_root_window(self):
        return self.winfo_toplevel()



    def _prepare_task(self):
        if not (len(self.input_files) >= 2 and self.output_file):
            messagebox.showerror(_("Input Incomplete"), _("Please add at least 2 files and select an output file."))
            return None

        target_function = pdf_merge_worker
        args_tuple = (self.input_files, self.output_file)
        initial_label = _("Preparing to merge...")

        return (target_function, args_tuple, initial_label)



    def add_files_to_list(self, file_paths):
        """辅助函数，用于添加文件列表 (来自对话框或拖放)"""
        count = 0
        for path in file_paths:
            path_lower = path.lower()
            if path_lower.endswith('.pdf') and path not in self.input_files:
                self.input_files.append(path)
                self.listbox.insert(tk.END, os.path.basename(path))
                count += 1



    def add_files_dialog(self):
        """'添加文件' 按钮的逻辑"""
        paths = filedialog.askopenfilenames(title=_("Select PDFs to merge"), filetypes=[(_("PDF Files"), "*.pdf")])
        self.add_files_to_list(paths)

    def on_drop_files(self, event):
        """拖放事件回调"""
        try:
            files = self.tk.splitlist(event.data)
            self.add_files_to_list(files)
        except Exception as e:
            print(f"Failed to parse drop event: {e}")
            messagebox.showerror(_("Drop Error"), _("Failed to process dropped files."))

    def remove_file(self):
        try:
            selected_indices = self.listbox.curselection()
            if not selected_indices: return
            for index in reversed(selected_indices):
                self.listbox.delete(index)
                self.input_files.pop(index)
        except Exception as e:
            pass
    def clear_files(self):
        self.listbox.delete(0, tk.END)
        self.input_files.clear()

    def select_output(self):
        path = filedialog.asksaveasfilename(title=_("Save Merged File As..."), filetypes=[(_("PDF Files"), "*.pdf")], defaultextension=".pdf")
        if path:
            self.output_file = path
            self.out_label.config(text=os.path.basename(path))