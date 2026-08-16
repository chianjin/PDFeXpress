import multiprocessing
import platform
from tkinter import ttk

from tkinterdnd2 import TkinterDnD

from config import EXECUTABLE_NAME, EXECUTABLE_PATH, PROJECT_NAME, PROJECT_VERSION
from core.main_frame import MainFrame
from widget.donate_dialog import maybe_show_donate

# Multiprocessing with freeze support
multiprocessing.freeze_support()


def main():
    system = platform.system()

    # High DPI (HiDPI) scaling issues On Windows
    if system == 'Windows':
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1 = System Aware
        except AttributeError:
            try:
                ctypes.windll.user32.SetProcessDPIAware()  # Fallback for older Windows
            except AttributeError:
                pass

    # TkinterDnD Root
    root = TkinterDnD.Tk()

    # Hide window
    root.withdraw()

    # Set window's title
    root.title(f'{PROJECT_NAME} - Ver. {PROJECT_VERSION}')

    # Set window's icon
    if system == 'Windows':
        root.iconbitmap(EXECUTABLE_PATH / f'asset/icon/{EXECUTABLE_NAME}.ico')
    elif system == 'Linux':
        theme_tcl = EXECUTABLE_PATH / 'asset/theme/breeze.tcl'
        root.call('source', str(theme_tcl))
        ttk.Style().theme_use('breeze')

    # Create MainFrame
    app = MainFrame(root)
    app.pack(fill='both', expand=True)

    # Wait for window to be fully initialized
    root.update_idletasks()

    # Set window size and position
    window_width = 1080
    window_height = 720
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 4
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    root.wm_resizable(False, False)

    # Show window
    root.deiconify()

    # Occasionally (≈10%) invite a donation; never blocks startup.
    root.after(1000, lambda: maybe_show_donate(root))

    root.mainloop()


if __name__ == '__main__':
    main()
