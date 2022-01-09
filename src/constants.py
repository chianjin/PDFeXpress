import gettext
import locale
from pathlib import Path

import psutil

DEFAULT_LANGUAGE = locale.getdefaultlocale()[0]
BASE_DIR = Path(__file__).absolute().parent
PHYSICAL_CPU_COUNT = psutil.cpu_count(logical=False)


APP_NAME = 'PDF eXpress'
APP_VERSION = '0.1-BETA'
APP_URL = 'https://github.com/chianjin/PDFeXpress'
APP_ICON = BASE_DIR / 'icon/PDFeXpress.ico'
INFO_ICON = BASE_DIR / 'icon/info32.png'

# TRANSLATER = gettext.gettext
TRANSLATER = gettext.translation(
        domain=APP_NAME.replace(' ', ''),
        localedir=str(BASE_DIR / 'locale'),
        languages=[DEFAULT_LANGUAGE, 'en_US']
        ).gettext
_ = TRANSLATER


SCREEN_RATIO = 3 / 5

BYTE_UNIT = ('', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')

FILE_TYPES_PDF = ((_('PDF File'), '*.pdf'),)
FILE_TYPES_TEXT = ((_('Text File'), '*.txt'),)
FILE_TYPES_IMAGE = (
        (_('Image File'), '*.jpg;*.jpeg;*.jp2;*.jp2000;*.png;*.gif;*.tif;*.tiff;*.bmp'),
        (_('JPEG Image'), '*.jpg;*.jpeg'),
        (_('PNG Image'), '*.png'),
        (_('GIF Image'), '*.gif'),
        (_('TIFF Image'), '*.tif;*.tiff'),
        (_('BMP Image'), '*.bmp')
        )
