import contextlib
import sys

from tkinterdnd2 import Tk

from config import APPLICATION_NAME, EXECUTABLE_NAME, ICONS_PATH
from ui.main_frame import MainFrame


def setup_dpi_awareness() -> None:
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            with contextlib.suppress(Exception):
                ctypes.windll.user32.SetProcessDPIAware()

def main() -> None:
    setup_dpi_awareness()

    root = Tk()
    root.title(APPLICATION_NAME)

    if sys.platform == 'win32':
        icon_path = ICONS_PATH / f'{EXECUTABLE_NAME}.ico'
        if icon_path.exists():
             root.iconbitmap(str(icon_path))

    app = MainFrame(root)
    app.pack(fill='both', expand=True)

    root.update_idletasks()
    req_width = root.winfo_reqwidth()
    req_height = root.winfo_reqheight()
    root.geometry(f'{req_width}x{req_height}')
    root.resizable(False, False)

    root.mainloop()


if __name__ == '__main__':
    main()
