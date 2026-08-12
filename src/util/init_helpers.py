import locale
import os
import sys

import darkdetect

from config import THEME_TCL


def setup_on_windows():
    import ctypes

    try:
        # fix High DPI (HiDPI) scaling issues in TkinterDnD2
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1 = System Aware
    except AttributeError:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # Fallback for older Windows
        except AttributeError:
            pass

    lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
    buffer = ctypes.create_unicode_buffer(85)
    ctypes.windll.kernel32.GetLocaleInfoW(lcid, 0x0000005C, buffer, 85)
    language = buffer.value.replace('-', '_')
    language = language if language else 'C'
    locale.setlocale(locale.LC_ALL, language)
    os.environ['LANG'] = language


def set_theme(root):
    root.tk.call('source', THEME_TCL)
    theme = darkdetect.theme().lower()
    root.tk.call('set_theme', theme)
    if sys.platform == 'win32':
        import pywinstyles

        pywinstyles.apply_style(root, theme)
