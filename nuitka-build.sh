#!/bin/sh
python -m nuitka --show-progress --show-memory --standalone \
 --include-data-dir=src/icon=icon --include-data-dir=src/locale=locale \
 --include-data-file=LICENSE=LICENSE --include-data-file=README.md=README.md --include-data-file=README.zh_CN.md=README.zh_CN.md \
 --plugin-enable=tk-inter --plugin-enable=multiprocessing \
 --output-dir=build src/PDFeXpress.py
