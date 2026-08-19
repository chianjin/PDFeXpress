import sys
from pathlib import Path

PROJECT_NAME = 'PDF eXpress'
PROJECT_VERSION = '2.0-BETA'
PROJECT_AUTHOR = 'chian.jin@gmail.com'
PROJECT_URL = 'https://github.com/chianjin/PDFeXpress'
PROJECT_UUID = '{2DA5BF84-B973-4D88-B278-EC0474D4BF3A}'

EXECUTABLE_NAME = PROJECT_NAME.replace(' ', '').lower()
try:
    EXECUTABLE_PATH = Path(sys._MEIPASS)
except AttributeError:
    EXECUTABLE_PATH = Path(__file__).resolve().parent
PROJECT_PATH = EXECUTABLE_PATH.parent

PAGE_RANGE_SYNTAX = 'page_range_syntax_guide-{}.txt'
PAGE_NUMBER_SYNTAX = 'page_number_syntax_guide-{}.txt'

HEADER_FONT_SIZE = 20
