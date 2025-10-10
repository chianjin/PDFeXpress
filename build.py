import os
import platform
import subprocess
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from setuptools.errors import PlatformError

from src.constant import APPLICATION_VERSION, EXECUTIVE_NAME

MACHINE_MAP = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "x64": "x86_64",
        "i386": "x86",
        "i686": "x86",
        "arm64": "arm64",
        "aarch64": "arm64",
    }

SYSTEM = platform.system()
MACHINE = platform.machine().lower()
MACHINE_TYPE = MACHINE_MAP.get(MACHINE, MACHINE)
ARCH = platform.architecture()[0][:2]

if ARCH == '32':
    raise PlatformError('x86 is not supported.')

PROJECT_DIR = Path(__file__).absolute().parent
SOURCE_DIR = PROJECT_DIR / 'src'
BUILD_DIR = PROJECT_DIR / 'build'
DIST_DIR = PROJECT_DIR  / 'dist' / EXECUTIVE_NAME
RELEASE_DIR = PROJECT_DIR / 'release'
RELEASE_DIR.mkdir(exist_ok=True)
RELEASE_DIR /= APPLICATION_VERSION
RELEASE_DIR.mkdir(exist_ok=True)


README_FILES = [
    'README.md', 'README.zh_CN.md',
    'CHANGELOG.md', 'CHANGELOG.zh_CN.md',
    'LICENSE'
]

def build():
    pyinstaller_cmd = [
        'pyinstaller',
        '-y',
        '--clean',
        f'{EXECUTIVE_NAME}.spec'
    ]

    process = subprocess.run(pyinstaller_cmd)
    if process.returncode != 0:
        raise ChildProcessError('PyInstaller building failed.')
    for file in README_FILES:
        shutil.copy(PROJECT_DIR / file, DIST_DIR)

    print('Building done.')


def create_portable():
    file_list = DIST_DIR.glob('**/*')
    # file_list.sort()
    portable_file = RELEASE_DIR / f'{EXECUTIVE_NAME}-{APPLICATION_VERSION}-Portable-{SYSTEM}-{MACHINE_TYPE}.zip'

    print('Creating portable package...')
    with ZipFile(portable_file, 'w', compression=ZIP_DEFLATED) as zf:
        for file in file_list:
            name_in_zip = file.relative_to(DIST_DIR)
            print(name_in_zip)
            if file.is_file():
                zf.write(file, name_in_zip)
    print('Creating portable package done.')


def update_iss():
    settings = {
        'APPLICATION_VERSION': APPLICATION_VERSION,
        'PROJECT_DIR': str(PROJECT_DIR),
        'MACHINE_TYPE': MACHINE_TYPE,
        }

    iss_template = f'{EXECUTIVE_NAME}-template.iss'
    iss_work = BUILD_DIR / f'{EXECUTIVE_NAME}-x64.iss'

    with open(iss_template) as template:
        iss_script = template.read()

    for key in settings:
        iss_script = iss_script.replace(f'%%{key}%%', settings.get(key))

    with open(iss_work, 'w') as iss:
        iss.write(iss_script)

    return iss_work


def check_iss():
    for environ_arg in ('ProgramFiles(x86)', 'ProgramFiles'):
        program_files = os.environ.get(environ_arg)
        iss_compiler = Path(program_files) / 'Inno Setup 6' / 'iscc.exe'
        if iss_compiler.exists():
            return iss_compiler
    return None


def create_setup():
    iss_work = update_iss()
    iss_compiler = check_iss()
    print(iss_work, iss_compiler)
    if iss_compiler:
        print('Creating Windows Installer...', end='')
        compiler_cmd = [str(iss_compiler), str(iss_work)]
        process = subprocess.run(compiler_cmd)
        if process.returncode != 0:
            raise ChildProcessError('Creating Windows installer failed.')
        print('done')


if __name__ == '__main__':
    import sys
    def __do_all():
        build()
        create_portable()
        if SYSTEM == 'Windows':
            create_setup()
        sys.exit(0)

    if len(sys.argv) == 1:
        __do_all()
    else:
        if sys.argv[1] == '--all':
            __do_all()
        elif sys.argv[1] == '--build':
            build()
            sys.exit(0)
        elif sys.argv[1] == '--portable':
            create_portable()
            sys.exit(0)
        elif sys.argv[1] == '--setup':
            if SYSTEM == 'Windows':
                create_setup()
                sys.exit(0)
            else:
                print('Setup is only supported on Windows.')
                sys.exit(1)


    if len(sys.argv) == 1:
        build()
        create_portable()
        if SYSTEM == 'Windows':
            create_setup()
        sys.exit(0)

    if len(sys.argv) > 1:



        if sys.argv[1] == '--portable':
            create_portable()
            sys.exit(0)
        elif sys.argv[1] == '--setup':
            if SYSTEM == 'Windows':
                create_setup()
                sys.exit(0)
            else:
                print('Setup is only supported on Windows.')
                sys.exit(1)
