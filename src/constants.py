import gettext
import locale
import os
import sys
from pathlib import Path

import psutil

BASE_DIR = Path(__file__).absolute().parent
PHYSICAL_CPU_COUNT = psutil.cpu_count(logical=False)

APP_NAME = 'PDF eXpress'
APP_VERSION = '0.1.1-BETA'
APP_URL = 'https://github.com/chianjin/PDFeXpress'
APP_ICON = BASE_DIR / 'icon/PDFeXpress32.png'

if 'win' in sys.platform:
    os.environ['LANGUAGE'] = locale.getdefaultlocale()[0]
gettext.install(domain=APP_NAME.replace(' ', ''), localedir=str(BASE_DIR / 'locale'))

SCREEN_RATIO = 1 / 2

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
