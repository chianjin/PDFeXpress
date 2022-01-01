from pathlib import Path

import psutil

BASE_DIR = Path(__file__).absolute().parent
PHYSICAL_CPU_COUNT = psutil.cpu_count(logical=False)

APP_NAME = 'PDF eXpress'
APP_VERSION = '0.1-BETA'
APP_URL = 'https://github.com/chianjin/PDFeXpress'
APP_ICON = BASE_DIR / 'PDFeXpress.ico'
SCREEN_RATIO = 2 / 3

BYTE_UNIT = ('', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')

FILE_TYPES_PDF = (('PDF 文件', '*.pdf'),)
FILE_TYPES_TEXT = (('文本文件', '*.txt'),)
FILE_TYPES_IMAGE = (
        ('图像文件', '*.jpg;*.jpeg;*.jp2;*.jp2000;*.png;*.gif;*.tif;*.tiff;*.bmp'),
        ('JPEG 图像', '*.jpg;*.jpeg'),
        ('PNG 图像', '*.png'),
        ('GIF 图像', '*.gif'),
        ('TIFF 图像', '*.tif;*.tiff'),
        ('BMP 图像', '*.bmp')
        )
