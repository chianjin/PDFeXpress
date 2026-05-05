"""PDF eXpress 主程序入口"""
import contextlib
import sys
from tkinter import ttk

from tkinterdnd2 import Tk

from config import APPLICATION_NAME, EXECUTABLE_NAME, ICONS_PATH
from ui.main_frame import MainFrame


def setup_dpi_awareness() -> None:
    """设置 Windows 平台高清 DPI 支持"""
    if sys.platform == 'win32':
        try:
            import ctypes
            # 设置 DPI 感知模式为 Per Monitor DPI Aware（每显示器 DPI 感知）
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            # 如果失败，尝试旧版 API
            with contextlib.suppress(Exception):
                ctypes.windll.user32.SetProcessDPIAware()

def set_style() -> None:
    """设置应用程序样式"""
    if sys.platform == 'linux':
        style = ttk.Style()
        style.theme_use('clam')


def main() -> None:
    """主函数"""
    # 设置 DPI 感知
    setup_dpi_awareness()

    # 创建根窗口（使用 tkinterdnd2 的 Tk 以支持拖拽）
    root = Tk()
    root.title(APPLICATION_NAME)

    # 设置窗口图标
    icon_path = ICONS_PATH / f'{EXECUTABLE_NAME}.ico'
    if icon_path.exists():
        root.iconbitmap(str(icon_path))

    # 设置应用程序样式
    set_style()

    # 创建主界面
    app = MainFrame(root)
    app.pack(fill='both', expand=True)

    # 设置窗口尺寸（禁止调整大小）
    root.update_idletasks()
    req_width = root.winfo_reqwidth()
    req_height = root.winfo_reqheight()
    root.geometry(f'{req_width}x{req_height}')
    root.resizable(False, False)  # 禁止调整窗口大小

    # 启动主循环
    root.mainloop()


if __name__ == '__main__':
    main()
