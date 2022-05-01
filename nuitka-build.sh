#!/bin/sh
if  [ "$1" != "" ] && [ "$1" != "--onefile" ]
then
  echo Usage: "$0" "[--onefile]"
  echo unkown option "$1"
  exit 1
fi

python -m nuitka "$1" --show-progress --show-memory --standalone \
 --include-data-dir=src/icon=icon --include-data-dir=src/locale=locale \
 --include-data-file=LICENSE=LICENSE --include-data-file=README.md=README.md \
 --include-data-file=README.zh_CN.md=README.zh_CN.md \
 --plugin-enable=tk-inter --output-dir=build src/PDFeXpress.py
