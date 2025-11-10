# toolkit/ui/feature/split_pdf.py

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from toolkit.constant import FILE_TYPES_PDF, HELP_ICON
from toolkit.page_range_syntax_help import PAGE_RANGE_SYNTAX_HELP
from toolkit.core.split_pdf_worker import split_pdf_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.folder_picker import FolderPicker
from toolkit.ui.widget.help_window import HelpWindow
from toolkit.ui.widget.misc import OptionFrame, TitleFrame


class SplitPDFApp(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)
        self.help_window = None

        self.columnconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)

        self.title_frame = TitleFrame(self, text=_("Split PDF"))
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        self.file_picker = FilePicker(
            self, title=_("Input PDF"), file_types=FILE_TYPES_PDF
        )
        self.file_picker.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

        self.output_folder_picker = FolderPicker(self, title=_("Output Folder"))
        self.output_folder_picker.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=(0, 5)
        )

        self.option_frame = OptionFrame(self, text=_("Options"))
        self.option_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))

        self.split_mode_var = tk.StringVar(value="single_page")
        self.split_mode_var.trace_add("write", self._on_split_mode_changed)

        modes = [
            (_("Single Page"), "single_page"),
            (_("By Pages of File"), "fixed_pages"),
            (_("By Number of Files"), "fixed_files"),
            (_("Custom Ranges"), "custom_ranges"),
        ]

        radio_frame = ttk.Frame(self.option_frame)
        radio_frame.pack(fill="x", padx=10, pady=5)
        for text, mode in modes:
            ttk.Radiobutton(
                radio_frame, text=_(text), variable=self.split_mode_var, value=mode
            ).pack(side="left", padx=5, pady=5)

        self.split_value_label = ttk.Label(radio_frame, text=_("Value:"))
        self.split_value_label.pack(side="left", padx=(10, 5), pady=5)
        self.icon = tk.PhotoImage(file=HELP_ICON)
        ttk.Button(
            radio_frame,
            image=self.icon,
            style='Toolbutton',
            cursor="hand2",
            command=self._show_syntax_help
        ).pack(side="left", padx=5, pady=0, anchor="center")


        self.split_value_var = tk.StringVar()
        self.split_value_entry = ttk.Entry(
            radio_frame, textvariable=self.split_value_var
        )
        self.split_value_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # 添加信息图标和描述文本
        description_frame = ttk.Frame(self.option_frame)
        description_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.fixed_description_label = ttk.Label(
            description_frame,
            text=_(
                "Value Description: By Pages/By Files: integer, e.g. 5  |  By Range: Supports multiple ranges (use ';' to split), page ranges (use '-' for range), optional start/end (e.g., '-10', '5-'), step (e.g., '1-10:3', ':3'), and duplicate pages (prefix with '+')"
            ),
            justify=tk.LEFT,
            wraplength=950
        )
        self.fixed_description_label.pack(side="left", fill="x", expand=True)

        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        self.start_button = ttk.Button(
            bottom_frame, text=_("Split"), command=self.run_task_from_ui
        )
        self.start_button.grid(row=0, column=1, padx=10, pady=5)

        self.file_picker.file_path_var.trace_add("write", self._on_input_pdf_changed)

        self._on_split_mode_changed()  # Initial state

    def _on_input_pdf_changed(self, *args):
        pdf_path_str = self.file_picker.get()
        if pdf_path_str:
            pdf_path = Path(pdf_path_str)
            # Extract filename without extension
            file_name_without_ext = pdf_path.stem
            # Construct new output folder name
            output_folder_name = f"{file_name_without_ext}_{_('Split')}"
            # Set the output folder picker's value
            output_dir = pdf_path.parent / output_folder_name
            self.output_folder_picker.set(str(output_dir))
        else:
            self.output_folder_picker.set("")

    def _on_split_mode_changed(self, *args):
        mode = self.split_mode_var.get()
        if mode == "single_page":
            self.split_value_entry.config(state="disabled")
        else:
            self.split_value_entry.config(state="normal")

    def _show_syntax_help(self, event=None):
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.lift()
            return
        self.help_window = HelpWindow(self, _("Page Range Syntax Guide"), PAGE_RANGE_SYNTAX_HELP, on_close=self.on_help_window_close)

    def on_help_window_close(self):
        self.help_window = None

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        pdf_path = self.file_picker.get()
        output_dir = self.output_folder_picker.get()
        split_mode = self.split_mode_var.get()
        split_value = self.split_value_var.get()

        if not pdf_path:
            messagebox.showerror(_("Invalid Input"), _("Please select an input PDF."))
            return None

        if not output_dir:
            messagebox.showerror(
                _("Invalid Input"), _("Please specify an output path.")
            )
            return None

        if (
            split_mode in ["fixed_pages", "fixed_files", "custom_ranges"]
            and not split_value
        ):
            messagebox.showerror(
                _("Invalid Input"), _("Please specify a value for the split mode.")
            )
            return None

        target_function = split_pdf_worker
        args_tuple = (pdf_path, output_dir, split_mode, split_value)
        initial_label = _("Splitting PDF...")

        return target_function, args_tuple, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)


if __name__ == "__main__":
    import tkinterdnd2
    root = tkinterdnd2.Tk()
    app = SplitPDFApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()