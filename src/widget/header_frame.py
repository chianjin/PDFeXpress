import tkinter as tk
from tkinter import ttk

from util.helpers import get_title_font


class HeaderFrame(ttk.Frame):
    def __init__(self, master: ttk.Frame, feature_id='', title='') -> None:
        super().__init__(master)

        # self._icon = self._load_function_icon(feature_id)

        ttk.Label(self, text=title, font=get_title_font()).pack(
            side=tk.RIGHT, padx=20, pady=(10, 0)
        )
        # ttk.Label(self, image=self._icon).pack(side=tk.RIGHT, pady=(10, 0))

    # def _load_function_icon(self, feature_id: str | None) -> tk.PhotoImage | None:
    #     if not feature_id:
    #         return None
    #
    #     icon_path = EXECUTABLE_PATH / f'asset/icon/feature/{feature_id}.png'
    #     if not icon_path.exists():
    #         icon_path = EXECUTABLE_PATH / 'asset/icon/feature/holder.png'
    #
    #     try:
    #         return tk.PhotoImage(file=icon_path)
    #     except Exception:
    #         return None
