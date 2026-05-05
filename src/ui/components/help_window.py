import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont


class HelpWindow(tk.Toplevel):
    """通用的说明帮助窗口"""

    def __init__(
        self,
        master,
        title: str,
        content: str,
        width: int = 650,
        height: int = 550,
    ):
        super().__init__(master)
        self.master = master
        self.title(title)
        self.geometry(f'{width}x{height}')
        self.minsize(400, 300)

        self._setup_ui(content)

    def _setup_ui(self, content):
        # 1. 底部按钮区域 (优先 pack，确保可见)
        footer_frame = ttk.Frame(self, padding=(0, 10))
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(footer_frame, text='关闭', command=self.destroy).pack()

        # 2. 中间内容容器
        container_frame = ttk.Frame(self, padding=10)
        container_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(container_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 获取系统默认字体
        try:
            default_font = tkfont.nametofont('TkDefaultFont')
            default_font_family = default_font.actual('family')
            default_font_size = default_font.actual('size')
        except Exception:
            default_font_family = 'Sans Serif'
            default_font_size = 10

        text_area = tk.Text(
            container_frame,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            font=(default_font_family, default_font_size),
            yscrollcommand=scrollbar.set,
            borderwidth=1,
            relief='solid',
        )
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_area.yview)

        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)
