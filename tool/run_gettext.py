import glob
import os
import pathlib
import sys

if sys.platform == 'win32':
    SYSTEM_PYTHON_BASE_DIR = pathlib.Path(sys.path[1]).parent
else:
    # TODO: Linux / FreeBSD
    SYSTEM_PYTHON_BASE_DIR = pathlib.Path('/usr/local/')


def run():
    python_scripts_list = glob.glob('../src/**/*.py', recursive=True)
    python_scripts_list = ' '.join(python_scripts_list)
    gettext_cmd = f'{SYSTEM_PYTHON_BASE_DIR}/Tools/i18n/pygettext.py -d PDFeXPress -p .. {python_scripts_list}'
    os.system(gettext_cmd)


if __name__ == '__main__':
    run()
