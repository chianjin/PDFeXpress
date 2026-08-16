import multiprocessing
import platform

from tkinterdnd2 import TkinterDnD

from config import EXECUTABLE_NAME, EXECUTIVE_PATH, PROJECT_NAME, PROJECT_VERSION
from core.main_frame import MainFrame

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
        try:
            root.iconbitmap(EXECUTIVE_PATH / f'asset/icon/{EXECUTABLE_NAME}.ico')
        except Exception:
            pass  # a missing icon must not prevent the app from starting

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
    root.mainloop()


if __name__ == '__main__':
    main()
