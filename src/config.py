from pathlib import Path

APPLICATION_NAME = 'PDF eXpress'
APPLICATION_VERSION = '1.9.1-alpha'
APPLICATION_URL = 'https://github.com/chianjin/PDFeXpress'

EXECUTABLE_NAME = APPLICATION_NAME.replace(' ', '').lower()

BASE_PATH = Path(__file__).resolve().parent
ASSETS_PATH = BASE_PATH / 'assets'
ICONS_PATH = ASSETS_PATH / 'icons'
FUNCTIONS_PATH = BASE_PATH / 'ui' / 'functions'
HELP_ICON = ICONS_PATH / 'help.png'

PAGE_RANGE_SYNTAX = ASSETS_PATH / 'page_range_syntax_guide.txt'
PAGE_NUMBER_SYNTAX = ASSETS_PATH / 'page_number_syntax_guide.txt'

# 标题字体配置
HEADER_FONT_SIZE = 20
