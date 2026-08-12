import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from typing import Literal

from tkinterdnd2 import DND_FILES, Tk

from util.file_types import FILE_TYPES
from util.helpers import filter_dropped_files, filter_dropped_folders
from util.i18n import gettext_text as _


class PathPicker(ttk.Frame):
    def __init__(
        self,
        master,
        base_frame=None,
        mode: Literal['save', 'open', 'folder'] = 'save',
        file_types: list[tuple[str, str]] = FILE_TYPES['PDF'],
        default_extension: str = '.pdf',
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        self._base_frame = base_frame
        self._mode = mode
        self._file_types = file_types
        self._default_extension = default_extension
        self._auto_output = True

        self._setup_ui()
        self._setup_drag_drop()

    def _setup_ui(self):
        self.path = tk.StringVar()

        ttk.Entry(self, textvariable=self.path).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(
            self,
            text=_('Browser'),
            command=self._open_path_dialog,
        ).pack(side=tk.LEFT, padx=(5, 0))

    def _open_path_dialog(self):
        path = ''
        match self._mode:
            case 'save':
                path = asksaveasfilename(
                    filetypes=self._file_types,
                    defaultextension=self._default_extension,
                    confirmoverwrite=True,
                )
            case 'open':
                path = askopenfilename(filetypes=self._file_types)
            case 'folder':
                path = askdirectory()

        if path:
            self.disable_auto_output()
            self.set_path(Path(path), force=True)

    def _setup_drag_drop(self):
        if self._mode in ('open', 'folder'):
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event):
        paths = None
        if self._mode == 'open':
            paths = filter_dropped_files(event, self._file_types)
        if self._mode == 'folder':
            paths = filter_dropped_folders(event)

    def get_path(self):
        return Path(self.path.get())

    def set_path(self, path, force=False):
        if not force and not self._auto_output:
            return
        self.path.set(str(path))


if __name__ == '__main__':
    root = Tk()
    PathPicker(root).pack(fill=tk.X, padx=5, pady=5)
    PathPicker(root, mode='open').pack(fill=tk.X, padx=5, pady=5)
    PathPicker(root, mode='folder').pack(fill=tk.X, padx=5, pady=5)
    root.mainloop()
