import tkinter as tk
from tkinter import ttk

from config import ICONS_PATH
from core.function_list import FUNCTION_LIST
from utils.helpers import get_title_font


class HeaderFrame(ttk.Frame):
    def __init__(self, master: ttk.Frame, function_id: str | None = None) -> None:
        super().__init__(master)

        title = FUNCTION_LIST[function_id].display_name

        self._icon = self._load_function_icon(function_id)

        ttk.Label(
            self, text=title, image=self._icon, compound=tk.LEFT, font=get_title_font()
        ).pack(side=tk.LEFT)

    def _load_function_icon(self, function_id: str | None) -> tk.PhotoImage | None:
        if not function_id:
            return None

        icon_path = ICONS_PATH / 'functions' / f'{function_id}.png'
        if not icon_path.exists():
            icon_path = ICONS_PATH / 'functions' / 'holder.png'

        try:
            return tk.PhotoImage(file=icon_path)
        except Exception:
            return None


if __name__ == '__main__':
    root = tk.Tk()
    root.title('HeaderFrame 测试')
    root.geometry('600x350')

    header1 = HeaderFrame(root, function_id='merge_pdf')
    header1.pack(fill=tk.X)

    header2 = HeaderFrame(root, function_id='nonexistent_function')
    header2.pack(fill=tk.X, pady=5)

    header3 = HeaderFrame(root)
    header3.pack(fill=tk.X, pady=5)

    root.mainloop()
