import gettext
import os
import platform

from config import EXECUTIVE_NAME

LOCALE_NAME_MAX_LENGTH = 85
LOCALE_DIR = "locale"


def _standardize_environment():
    if "LANG" in os.environ:
        return
    if platform.system() == "Windows":
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
            kernel32 = ctypes.windll.kernel32
            if kernel32.GetUserDefaultLocaleName(buffer, LOCALE_NAME_MAX_LENGTH):
                posix_code = buffer.value.replace("-", "_")
                os.environ["LANG"] = f"{posix_code}.UTF-8"
        except (OSError, AttributeError, ImportError, ctypes.WinError):
            pass


_standardize_environment()

gettext.bindtextdomain(EXECUTIVE_NAME, LOCALE_DIR)
gettext.textdomain(EXECUTIVE_NAME)
translation = gettext.translation(EXECUTIVE_NAME, LOCALE_DIR, fallback=True)

gettext_text = translation.gettext
ngettext = translation.ngettext
