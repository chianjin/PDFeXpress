# src/toolkit/ui/feature/to_image.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from tkinterdnd2 import DND_FILES

# (关键) 导入框架、业务逻辑和翻译
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.core.pdf_to_image_worker import pdf_to_image_worker
from toolkit.i18n import gettext_text as _

class PdfToImageApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, padding="20", **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)

        self.pdf_path = None
        self.output_dir = None 

        # --- GUI ---
        self.select_button = ttk.Button(self, text=_("1. Select PDF File"), command=self.select_pdf)
        self.select_button.pack(pady=(5,0), fill=tk.X)
        self.path_label = ttk.Label(self, text=_("No file selected (or drag file here)"), wraplength=350)
        self.path_label.pack(pady=(2,5), fill=tk.X)

        self.select_dir_button = ttk.Button(self, text=_("2. Select Output Folder"), command=self.select_directory)
        self.select_dir_button.pack(pady=5, fill=tk.X)
        self.dir_label = ttk.Label(self, text=_("No folder selected"), wraplength=350)
        self.dir_label.pack(pady=(2,5), fill=tk.X)

        options_frame = ttk.LabelFrame(self, text=_("3. Optimization Options"))
        options_frame.pack(fill=tk.X, pady=5, ipady=5)
        ttk.Label(options_frame, text=_("Image Quality (DPI):")).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.dpi_var = tk.StringVar(value="150")
        self.dpi_entry = ttk.Entry(options_frame, textvariable=self.dpi_var, width=10)
        self.dpi_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(options_frame, text=_("Image Format:")).grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.format_var = tk.StringVar(value="png")
        self.format_menu = ttk.Combobox(options_frame, textvariable=self.format_var, values=["png", "jpg"], state="readonly", width=7)
        self.format_menu.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        options_frame.columnconfigure(1, weight=1)

        # 底部操作和状态区域
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1) # 按钮列
        bottom_frame.columnconfigure(1, weight=3) # 状态栏列

        # 执行按钮
        self.start_button = ttk.Button(
            bottom_frame,
            text=_("4. Start Conversion"),
            command=self.run_task_from_ui
        )
        self.start_button.grid(row=0, column=0, padx=(0, 5), sticky=tk.W+tk.E)

        # 状态栏
        self.status_label = ttk.Label(
            bottom_frame,
            text=_("Ready"),
            anchor=tk.W,
            relief=tk.SUNKEN # 增加视觉效果
        )
        self.status_label.grid(row=0, column=1, sticky=tk.W+tk.E)

        # (关键) 注册整个 Frame 为拖放目标
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop_pdf)

    # --- 实现 Mixin "契约" ---
    def _get_root_window(self):
        return self.winfo_toplevel() 



    def _prepare_task(self):
        if not self.pdf_path or not self.output_dir:
            messagebox.showerror(_("Input Incomplete"), _("Please select a PDF file and an output folder."))
            return None
        try:
            dpi_value = int(self.dpi_var.get())
            if not 1 <= dpi_value <= 600: raise ValueError(_("DPI must be between 1 and 600"))
        except ValueError as e:
            messagebox.showerror(_("Invalid Input"), _("Invalid DPI value: {}").format(e))
            return None
        image_format = self.format_var.get()

        target_function = pdf_to_image_worker
        args_tuple = (self.pdf_path, self.output_dir, dpi_value, image_format)
        initial_label = _("Opening PDF...")

        return (target_function, args_tuple, initial_label)

    def update_status(self, message):
        self.status_label.config(text=message)





    def set_pdf_path(self, path):
        """辅助函数，用于设置 PDF 路径"""
        if path.lower().endswith('.pdf'):
            self.pdf_path = path
            self.path_label.config(text=f"{_('Selected')}: {Path(path).name}")

        else:
            messagebox.showwarning(_("Invalid File"), _("Please drop a single PDF file."))

    def select_pdf(self):
        path = filedialog.askopenfilename(title=_("Select a PDF File"), filetypes=[(_("PDF Files"), "*.pdf")])
        if path:
            self.set_pdf_path(path)

    def select_directory(self):
        path = filedialog.askdirectory(title=_("Select an Output Folder"))
        if path:
            self.output_dir = path
            self.dir_label.config(text=f"{_('Output to')}: {path}")


    def on_drop_pdf(self, event):
        """拖放事件回调"""
        try:
            files = self.tk.splitlist(event.data)
            if not files: return
            first_file = files[0] # 此功能只接受一个文件
            print(f"File dropped: {first_file}")
            self.set_pdf_path(first_file)
        except Exception as e:
            print(f"Failed to parse drop event: {e}")
            messagebox.showerror(_("Drop Error"), _("Failed to process dropped file."))