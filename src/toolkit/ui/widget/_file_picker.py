# toolkit/ui/widget/_file_picker.py
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from toolkit.i18n import gettext_text as _
from toolkit.constant import FILE_TYPES_PDF
from toolkit.util.file_util import get_files_with_extensions
from toolkit.util.decorator import create_run_after_decorator

check_file_path_change = create_run_after_decorator("_on_change_callback")

class FilePicker(ttk.Labelframe):
    """文件选择组件，支持open和save两种模式"""
    def __init__(
            self, parent, title=_("Input File"),
            mode="open", file_types=FILE_TYPES_PDF,
            on_change_callback=None,
            **kwargs
        ):
        super().__init__(parent, text=title, **kwargs)
        self._on_change_callback = on_change_callback

        self.file_path_var = tk.StringVar()

        self._mode = mode # open or save
        self._file_types = file_types

        self.columnconfigure(0, weight=1)
        self.file_path_entry = ttk.Entry(
            self, textvariable=self.file_path_var, state="readonly"
        )
        self.file_path_entry.grid(row=0, column=0, sticky="we", padx=5, pady=5)

        self.browse_button = ttk.Button(
            self, text=_('Browse'), command=self._on_browse_file
        )
        self.browse_button.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        if self._mode == "open":
            self.drop_target_register(tkinterdnd2.DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)

    @check_file_path_change
    def _open_file(self):
        file_path = filedialog.askopenfilename(
            title=_("Select input file."),
            filetypes=self._file_types,
        )
        if file_path:
            self.file_path_var.set(str(Path(file_path)))

    @check_file_path_change
    def _save_file(self):
        file_path = filedialog.asksaveasfilename(
            title=_("Select output file."),
            filetypes=self._file_types,
            confirmoverwrite=True,
        )
        if file_path:
            self.file_path_var.set(str(Path(file_path)))

    def _on_browse_file(self):
        """处理文件选择按钮点击事件"""
        if self._mode == "open":
            self._open_file()
        elif self._mode == "save":
            self.file_path_entry.config(state="normal")
            self._save_file()

    @check_file_path_change
    def _on_drop(self, event):
        if self._mode == "open":
            toplevel = self.winfo_toplevel()
            file_list = toplevel.tk.splitlist(event.data)
            file_path = get_files_with_extensions(file_list, self._file_types)[0]
            if file_path:
                self.file_path_var.set(str(Path(file_path)))
        return None

    def get(self):
        return self.file_path_var.get()

    def set(self, path):
        self.file_path_var.set(path)

    def clear(self):
        self.file_path_var.set("")


if __name__ == "__main__":
    # 测试文件选择组件
    import tkinterdnd2
    root = tkinterdnd2.Tk()
    root.title("File Selector Test")
    root.geometry("500x150")
    
    # 测试open模式
    open_selector = FilePicker(root, title="输入文件", mode="open")
    open_selector.pack(fill="x", padx=10, pady=5)
    
    # 测试save模式
    save_selector = FilePicker(root, title="输出文件", mode="save")
    save_selector.pack(fill="x", padx=10, pady=5)
    
    root.mainloop()