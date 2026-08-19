import sys
from pathlib import Path

PROJECT_NAME = 'PDF eXpress'
PROJECT_VERSION = '2.0-BETA'
PROJECT_AUTHOR = 'chian.jin@gmail.com'
PROJECT_URL = 'https://github.com/chianjin/PDFeXpress'
PROJECT_UUID = '{2DA5BF84-B973-4D88-B278-EC0474D4BF3A}'

# 更新检测相关配置（链接 / 行为变更只需改这里）。
LATEST_VERSION_URL = 'https://raw.giteeusercontent.com/jinchian/PDFeXpress/raw/main/LATEST-VERSION'
QUARK_DOWNLOAD_URL = 'https://pan.quark.cn/s/abc772612ee5?pwd=97sh'
BAIDU_DOWNLOAD_URL = 'https://pan.baidu.com/s/14I_0RdbfVqpWORXfgYlEjQ?pwd=i4xb'
UPDATE_RECHECK_DAYS = 15  # 「以后再说」后，多少天重新弹更新框

EXECUTABLE_NAME = PROJECT_NAME.replace(' ', '').lower()
try:
    EXECUTABLE_PATH = Path(sys._MEIPASS)
except AttributeError:
    EXECUTABLE_PATH = Path(__file__).resolve().parent
PROJECT_PATH = EXECUTABLE_PATH.parent

PAGE_RANGE_SYNTAX = 'page_range_syntax_guide-{}.txt'
PAGE_NUMBER_SYNTAX = 'page_number_syntax_guide-{}.txt'

HEADER_FONT_SIZE = 20
