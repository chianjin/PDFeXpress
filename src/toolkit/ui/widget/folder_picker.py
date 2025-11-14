import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from toolkit.i18n import gettext_text as _


class FolderPicker(ttk.Labelframe):
    def __init__(self, parent, title=_("Output Folder"), **kwargs):
        super().__init__(parent, text=title, **kwargs)

        self.folder_path_var = tk.StringVar()
        self.folder_path_entry = ttk.Entry(
            self,
            textvariable=self.folder_path_var,
        )
        self.folder_path_entry.grid(row=0, column=0, sticky="we", padx=5, pady=5)

        self.browse_button = ttk.Button(
            self, text=_("Browse"), command=self._browse_folder
        )
        self.browse_button.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.columnconfigure(0, weight=1)

    def _browse_folder(self):
        """Browse for a folder."""
        folder_path = filedialog.askdirectory(title=_("Select Path"), mustexist=True)
        if folder_path:
            self.folder_path_var.set(str(Path(folder_path)))

    def get(self):
        return self.folder_path_var.get()

    def set(self, path):
        self.folder_path_var.set(path)

    def clear(self):
        self.folder_path_var.set("")

    def set_state(self, state):
        self.folder_path_entry.config(state=state)
        self.browse_button.config(state=state)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Folder Selector Test")
    root.geometry("500x100")

    folder_selector = FolderPicker(root, title="Output Folder")
    folder_selector.pack(fill="x", padx=10, pady=10)

    root.mainloop()
