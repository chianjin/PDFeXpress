from pathlib import Path

PROJECT_NAME = 'PDF eXpress'
PROJECT_VERSION = '1.9.1-alpha'
PROJECT_AUTHOR = 'chian.jin@gmail.com'
PROJECT_URL = 'https://github.com/chianjin/PDFeXpress'
PROJECT_UUID = '{2DA5BF84-B973-4D88-B278-EC0474D4BF3A}'

EXECUTABLE_NAME = PROJECT_NAME.replace(' ', '').lower()
EXECUTIVE_PATH = Path(__file__).resolve().parent
PROJECT_PATH = EXECUTIVE_PATH.parent

PAGE_RANGE_SYNTAX = 'page_range_syntax_guide-{}.txt'
PAGE_NUMBER_SYNTAX = 'page_number_syntax_guide-{}.txt'

HEADER_FONT_SIZE = 20

MAIN_FRAME_COLUMNS = 3
