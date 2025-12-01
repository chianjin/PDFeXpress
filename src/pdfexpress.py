import multiprocessing
import platform
from tkinter import TclError
import tkinter.font as tkfont

from tkinterdnd2 import TkinterDnD

from config import EXECUTIVE_NAME, PROJECT_NAME, PROJECT_VERSION
from toolkit.main_frame import MainFrame

system = platform.system()

if __name__ == '__main__':
    if system == 'Windows':
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(True)

    multiprocessing.freeze_support()

    root = TkinterDnD.Tk()
    root.title(f'{PROJECT_NAME} - Ver. {PROJECT_VERSION}')

    if system == 'Windows':
        icon_path = f'data/{EXECUTIVE_NAME}.ico'
        root.iconbitmap(icon_path)
    else:
        from ttkthemes import ThemedStyle
        tkfont.nametofont('TkDefaultFont').configure(size=12)
        style = ThemedStyle(root)
        try:
            style.set_theme('plastik')
        except TclError:
            style.set_theme('clam')

    window_width = 960
    window_height = 640
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 4
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    app = MainFrame(root)
    root.mainloop()
