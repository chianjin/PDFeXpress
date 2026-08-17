"""i18n management for PDF eXpress (Babel).

Wraps the pybabel commands so the long argument lists don't have to be
memorized. Run from the repository root (flags can be combined):

    python i18n.py -e        # regenerate src/locale/pdfexpress.pot
    python i18n.py -u        # merge new strings into existing .po files
    python i18n.py -c        # compile .po -> .mo (what the app loads)
    python i18n.py -a        # extract + update + compile
    python i18n.py -e -c     # combine flags
"""

import argparse
import subprocess
import sys
from pathlib import Path

from src.config import EXECUTABLE_NAME, PROJECT_AUTHOR, PROJECT_NAME, PROJECT_VERSION

PROJECT_DIR = Path(__file__).parent.resolve()
SRC_DIR = PROJECT_DIR / 'src'
LOCALE_DIR = SRC_DIR / 'locale'
BABEL_CFG = PROJECT_DIR / 'babel.cfg'
DOMAIN = EXECUTABLE_NAME  # 'pdfexpress'
POT_FILE = LOCALE_DIR / f'{DOMAIN}.pot'


def _run(command):
    """Run a pybabel command, surfacing its output on success/failure."""
    print(f'Running: {" ".join(command)}')
    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, encoding='utf-8'
        )
    except subprocess.CalledProcessError as e:
        print('Command failed.')
        if e.stdout:
            print(f'Stdout: {e.stdout}')
        if e.stderr:
            print(f'Stderr: {e.stderr}')
        raise
    except FileNotFoundError:
        print(
            "Error: 'pybabel' not found. Install Babel via "
            '`pip install -r requirements-dev`.'
        )
        raise
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())


def extract():
    print('\n--- Extracting translatable strings (POT) ---')
    command = [
        'pybabel',
        'extract',
        '-F',
        str(BABEL_CFG),
        '--project',
        PROJECT_NAME,
        '--version',
        PROJECT_VERSION,
        '--copyright-holder',
        PROJECT_AUTHOR,
        '--msgid-bugs-address',
        PROJECT_AUTHOR,
        '-o',
        str(POT_FILE),
        str(SRC_DIR),
    ]
    _run(command)
    print(f'Template written to {POT_FILE}')


def update():
    print('\n--- Updating translations (PO) ---')
    command = [
        'pybabel',
        'update',
        '-i',
        str(POT_FILE),
        '-d',
        str(LOCALE_DIR),
        '-D',
        DOMAIN,
    ]
    _run(command)


def compile_catalog():
    print('\n--- Compiling translations (MO) ---')
    command = [
        'pybabel',
        'compile',
        '-d',
        str(LOCALE_DIR),
        '-D',
        DOMAIN,
    ]
    _run(command)
    print('Compile finished.')


def all_steps():
    extract()
    update()
    compile_catalog()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='i18n management for PDF eXpress (Babel).'
    )
    parser.add_argument(
        '-e', '--extract', action='store_true', help='Regenerate the .pot template from source strings.'
    )
    parser.add_argument(
        '-u', '--update', action='store_true', help='Merge new strings into existing .po files.'
    )
    parser.add_argument(
        '-c', '--compile', action='store_true', help='Compile .po files to .mo (what the app loads).'
    )
    parser.add_argument(
        '-a', '--all', action='store_true', help='Run extract + update + compile.'
    )

    args = parser.parse_args()

    if not any([args.extract, args.update, args.compile, args.all]):
        parser.print_help()
        sys.exit(1)

    if args.all:
        all_steps()
    else:
        if args.extract:
            extract()
        if args.update:
            update()
        if args.compile:
            compile_catalog()

    print('\ni18n script finished.')
