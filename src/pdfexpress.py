# src/pdfexpress.py
import platform
import multiprocessing

from tkinterdnd2 import TkinterDnD

from config import PROJECT_NAME, PROJECT_VERSION, EXECUTIVE_NAME
from toolkit.main_frame import MainFrame

system = platform.system()

if __name__ == "__main__":

    if system == "Windows":
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

    multiprocessing.freeze_support()

    root = TkinterDnD.Tk()
    root.title(f'{PROJECT_NAME} - Ver. {PROJECT_VERSION}')

    if system == 'Windows':
        icon_path = f"data/{EXECUTIVE_NAME}.ico"
        root.iconbitmap(icon_path)
    else:
        from ttkthemes import ThemedStyle
        style = ThemedStyle(root)
        try:
            style.set_theme('plastik')
        except:
            style.set_theme('clam')

    # Center the window
    window_width = 1280
    window_height = 768
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 4
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    app = MainFrame(root)
    root.mainloop()