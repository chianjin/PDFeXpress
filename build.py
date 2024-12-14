import os
import platform
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from setuptools.errors import PlatformError

from src.constant import APPLICATION_VERSION, EXECUTIVE_NAME

SYSTEM = platform.system()
ARCH = platform.architecture()[0][:2]

if ARCH == '32':
    raise PlatformError('x86 is not supported.')

PROJECT_DIR = Path(__file__).absolute().parent
SOURCE_DIR = Path('src')
BUILD_DIR = Path('build')
OUTPUT_DIR = BUILD_DIR
RELEASE_DIR = Path('release') / APPLICATION_VERSION
if not RELEASE_DIR.exists():
    RELEASE_DIR.mkdir()


def build():
    nuitka_cmd = [
        'nuitka',
        '--clang',
        '--mingw64',
        # '--show-progress',
        '--show-memory',
        '--standalone',
        '--include-data-dir=src/data=data',
        '--include-data-dir=src/locale=locale',
        '--include-data-file=LICENSE=LICENSE',
        '--include-data-file=README.md=README.md',
        '--include-data-file=README.zh_CN.md=README.zh_CN.md',
        '--plugin-enable=tk-inter',
        f'--output-dir={OUTPUT_DIR}'
    ]

    if platform.system() == 'Windows':
        nuitka_cmd.extend(
            (
                '--windows-disable-console',
                '--windows-icon-from-ico=src/data/PDFeXpress.ico',
            )
        )
    nuitka_cmd.append(SOURCE_DIR / f'{EXECUTIVE_NAME}.py')

    process = subprocess.run(nuitka_cmd, shell=True)
    if process.returncode != 0:
        raise ChildProcessError('Nuitka building failed.')

    print('Building done.')


def create_portable():
    dist_dir = OUTPUT_DIR / f'{EXECUTIVE_NAME}.dist'
    file_list = dist_dir.glob('**/*')
    # file_list.sort()
    portable_file = RELEASE_DIR / f'{EXECUTIVE_NAME}-{APPLICATION_VERSION}-Portable-{SYSTEM}-{ARCH}.zip'

    print('Creating portable package...')
    with ZipFile(portable_file, 'w', compression=ZIP_DEFLATED) as zf:
        for file in file_list:
            name_in_zip = file.relative_to(dist_dir)
            print(name_in_zip)
            if file.is_file():
                zf.write(file, name_in_zip)
    print('Creating portable package done.')


def update_iss():
    settings = {
        'APP_VERSION': APPLICATION_VERSION,
        'PROJECT_DIR': str(PROJECT_DIR),
        'OUTPUT_DIR': str(OUTPUT_DIR),
        'RELEASE_DIR': str(RELEASE_DIR),
        'ARCH': ARCH,
        'ARCH_MODE': 'ArchitecturesInstallIn64BitMode=x64' if ARCH == '64' else ''
    }

    iss_template = f'{EXECUTIVE_NAME}-template.iss'
    iss_work = Path(BUILD_DIR) / f'{EXECUTIVE_NAME}-{ARCH}.iss'

    with open(iss_template) as template:
        iss_script = template.read()

    for key in settings:
        iss_script = iss_script.replace(f'%%{key}%%', settings.get(key))

    with open(iss_work, 'w') as iss:
        iss.write(iss_script)

    return iss_work


def check_iss():
    if ARCH == '64':
        program_files = os.environ.get('ProgramFiles(x86)')
    else:
        program_files = os.environ.get('ProgramFiles')
    iss_compiler = Path(program_files) / 'Inno Setup 6' / 'Compil32.exe'

    if iss_compiler.exists():
        return iss_compiler
    return None


def create_setup():
    iss_work = update_iss()
    iss_compiler = check_iss()
    if iss_compiler:
        print('Creating Windows Installer...', end='')
        compiler_cmd = [str(iss_compiler), '/cc', str(iss_work)]
        process = subprocess.run(compiler_cmd)
        if process.returncode != 0:
            raise ChildProcessError('Creating Windows installer failed.')
        print('done')


if __name__ == '__main__':
    # build()
    create_portable()
    # if SYSTEM == 'Windows':
    #     create_setup()
