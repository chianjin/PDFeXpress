"""头部框架组件"""

import tkinter as tk
from tkinter import ttk

from config import ICONS_PATH
from core.function_list import FUNCTION_LIST
from utils.helpers import get_title_font


class HeaderFrame(ttk.Frame):
    """头部框架组件

    显示功能图标和功能名称，用于各个功能界面的顶部。
    """

    def __init__(self, master: ttk.Frame, function_id: str | None = None) -> None:
        """初始化头部框架

        Args:
            master: 父容器
            function_id: 功能 ID（用于自动推导图标和标题）
        """
        super().__init__(master)

        # 从 FUNCTION_LIST 获取显示名称
        title = FUNCTION_LIST[function_id].display_name

        # 加载图标
        self._icon = self._load_function_icon(function_id)

        # 标题标签
        ttk.Label(
            self, text=title, image=self._icon, compound=tk.LEFT, font=get_title_font()
        ).pack(side=tk.LEFT)

    def _load_function_icon(self, function_id: str | None) -> tk.PhotoImage | None:
        """加载功能图标

        根据 function_id 自动推导图标文件名，如果找不到则使用占位符。

        Args:
            function_id: 功能 ID（如 'merge_pdf'）

        Returns:
            PhotoImage 对象，如果加载失败则返回 None
        """
        if not function_id:
            return None

        # 尝试加载功能图标
        icon_path = ICONS_PATH / 'functions' / f'{function_id}.png'
        if not icon_path.exists():
            icon_path = ICONS_PATH / 'functions' / 'holder.png'

        try:
            return tk.PhotoImage(file=icon_path)
        except Exception:
            return None


if __name__ == '__main__':
    # 单独测试代码
    root = tk.Tk()
    root.title('HeaderFrame 测试')
    root.geometry('600x350')

    # 测试1：有效的 function_id
    header1 = HeaderFrame(root, function_id='merge_pdf')
    header1.pack(fill=tk.X)

    # 测试2：不存在的 function_id（使用占位符图标，默认标题）
    header2 = HeaderFrame(root, function_id='nonexistent_function')
    header2.pack(fill=tk.X, pady=5)

    # 测试3：没有 function_id（不显示图标，默认标题）
    header3 = HeaderFrame(root)
    header3.pack(fill=tk.X, pady=5)

    root.mainloop()
