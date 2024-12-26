import gettext
import locale
import os
import platform
from collections import namedtuple
from pathlib import Path

# import psutil

APPLICATION_NAME = 'PDF eXpress'
EXECUTIVE_NAME = APPLICATION_NAME.replace(' ', '')
APPLICATION_VERSION = '0.4.1.1-BETA'
APPLICATION_URL = f'https://github.com/chianjin/{EXECUTIVE_NAME}'

SYSTEM = platform.system()
# PHYSICAL_CPU_COUNT = psutil.cpu_count(logical=False)
BASE_FOLDER = Path(__file__).absolute().parent

BYTE_UNIT = ('', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')

if SYSTEM == 'Windows':
    os.environ['LANGUAGE'] = locale.getdefaultlocale()[0]
gettext.install(domain=EXECUTIVE_NAME, localedir=str(BASE_FOLDER / 'locale'))

FILE_WILDCARD = {
    'all': ((_('All Files'), '*.*'),),
    'text': ((_('Text File'), '*.txt'),),
    'pdf': ((_('PDF File'), '*.pdf'),),
    'jpg': ((_('JPEG Image'), '*.jpg;*.jpeg'),),
    'image': (
        (_('Image File'), '*.jpg;*.jpeg;*.png;*.gif;*.tif;*.tiff;*.bmp'),
        (_('JPEG Image'), '*.jpg;*.jpeg'),
        (_('PNG Image'), '*.png'),
        (_('GIF Image'), '*.gif'),
        (_('TIFF Image'), '*.tif;*.tiff'),
        (_('BMP Image'), '*.bmp'),
        (_('WebP Image'), '*.webp'),
    )
}
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff', '.bmp')

file_label = namedtuple('file_label', ['label', 'prompt', 'extension', 'wildcard'])

FILE_LABELS = {
    'all': file_label(_('Output File'), _('Select File'), '.*', '*.*'),
    'pdf': file_label(_('PDF Output File'), _('Select PDF File'), '.pdf', ((_('PDF File'), '*.pdf'),)),
    'text': file_label(_('Text Output File'), _('Select Text File'), '.txt', ((_('Text File'), '*.txt'),))
}
