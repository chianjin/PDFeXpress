import importlib
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Any

from config import APPLICATION_NAME, EXECUTABLE_NAME, FUNCTIONS_PATH, ICONS_PATH
from core.function_list import FUNCTION_LIST
from utils.helpers import get_title_font


class MainFrame(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=10)
        self._function_frames: dict[str, Any] = {}
        self._create_widgets()

    def _create_widgets(self) -> None:
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill=tk.X)

        app_icon_path = ICONS_PATH / f'{EXECUTABLE_NAME}.png'
        app_icon = self._load_icon(app_icon_path)

        icon_label = ttk.Label(header_frame, image=app_icon)
        icon_label.image = app_icon
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        title_label = ttk.Label(header_frame, text=APPLICATION_NAME, font=get_title_font())
        title_label.pack(side=tk.LEFT)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.BOTH, expand=True)

        self._create_function_buttons(button_frame)

        self._configure_grid_weights(button_frame)

    def _configure_grid_weights(self, master: ttk.Frame) -> None:
        max_col = max(func.column for func in FUNCTION_LIST.values()) + 1
        max_row = max(func.row for func in FUNCTION_LIST.values()) + 1

        for col in range(max_col):
            master.columnconfigure(col, weight=1)
        for row in range(max_row):
            master.rowconfigure(row, weight=1)

    def _create_function_buttons(self, master: ttk.Frame) -> None:
        for function_id, func in FUNCTION_LIST.items():
            button = self._create_function_button(master, function_id, func.display_name)
            padx = 0 if func.column == 0 else (2, 0)
            pady = 0 if func.row == 0 else (2, 0)
            button.grid(row=func.row, column=func.column, padx=padx, pady=pady, sticky='nsew')

    def _create_function_button(
        self, master: ttk.Frame, function_id: str, display_name: str
    ) -> ttk.Button:
        is_available = self._load_function(function_id)

        icon_path = self._get_icon_path(function_id)
        icon_image = self._load_icon(icon_path)

        button = ttk.Button(
            master,
            text=display_name,
            image=icon_image,
            compound=tk.TOP,
            command=lambda fid=function_id: self._open_function(fid) if is_available else None,
            state=tk.NORMAL if is_available else tk.DISABLED,
        )

        button.image = icon_image

        return button

    def _get_icon_path(self, function_id: str) -> Path:
        icon_filename = f'{function_id}.png'
        icon_path = ICONS_PATH / 'functions' / icon_filename

        if not icon_path.exists():
            icon_path = ICONS_PATH / 'functions' / 'holder.png'

        return icon_path

    def _load_icon(self, icon_path: Path) -> tk.PhotoImage:
        try:
            return tk.PhotoImage(file=str(icon_path))
        except Exception:
            return tk.PhotoImage(width=32, height=32)

    def _load_function(self, function_id: str) -> bool:
        if function_id in self._function_frames:
            return True

        try:
            module_filename = f'{function_id}_frame.py'
            module_path = FUNCTIONS_PATH / module_filename

            if not module_path.exists():
                return False

            module_path_str = f'ui.functions.{function_id}_frame'
            class_name = f'{function_id.title().replace("_", "")}Frame'

            module = importlib.import_module(module_path_str)
            frame_class = getattr(module, class_name)

            self._function_frames[function_id] = frame_class
            return True

        except Exception:
            return False

    def _open_function(self, function_id: str) -> None:
        if function_id not in self._function_frames:
            return

        display_name = FUNCTION_LIST[function_id][0]

        top_window = tk.Toplevel(self)
        top_window.title(display_name)
        top_window.transient(self)
        top_window.focus()
        top_window.configure(padx=10, pady=10)

        frame_class = self._function_frames[function_id]
        frame = frame_class(top_window)
        frame.pack(fill=tk.BOTH, expand=True)

        top_window.update_idletasks()
        min_height = top_window.winfo_reqheight()
        top_window.minsize(900, min_height)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 900
        x = (screen_width - window_width) // 2
        y = (screen_height - min_height) // 4
        top_window.geometry(f'{window_width}x{min_height}+{x}+{y}')


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    root.title(APPLICATION_NAME)
    app = MainFrame(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()
    min_width = root.winfo_reqwidth()
    min_height = root.winfo_reqheight()
    root.minsize(min_width, min_height)
    root.mainloop()
