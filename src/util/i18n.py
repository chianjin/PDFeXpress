import gettext
import locale
import os
import platform

from config import EXECUTABLE_NAME, EXECUTABLE_PATH

LOCALE_NAME_MAX_LENGTH = 85
LOCALE_DIR = EXECUTABLE_PATH / 'locale'


def _standardize_environment():
    if 'LANG' in os.environ:
        return
    if platform.system() == 'Windows':
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
            kernel32 = ctypes.windll.kernel32
            if kernel32.GetUserDefaultLocaleName(buffer, LOCALE_NAME_MAX_LENGTH):
                posix_code = buffer.value.replace('-', '_')
                locale.setlocale(locale.LC_ALL, f'{posix_code}.UTF-8')
                os.environ['LANG'] = f'{posix_code}'
        except (OSError, AttributeError, ImportError, ctypes.WinError):
            pass


_standardize_environment()

gettext.bindtextdomain(EXECUTABLE_NAME, LOCALE_DIR)
gettext.textdomain(EXECUTABLE_NAME)
translation = gettext.translation(EXECUTABLE_NAME, LOCALE_DIR, fallback=True)

gettext_text = translation.gettext
