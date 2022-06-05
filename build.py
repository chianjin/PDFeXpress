import glob
import os
import platform
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from src.constants import APP_VERSION, EXEC_NAME

SYSTEM = platform.system()
MACHINE = platform.machine().lower()
if MACHINE == 'amd64':
    MACHINE = 'x64'

PROJECT_DIR = Path(__file__).absolute().parent
BUILD_DIR = 'build'
RELEASE_DIR = 'release'
OUTPUT_DIR = f'{BUILD_DIR}/{SYSTEM}-{MACHINE}'


def build():
    nuitka_cmd = [
            'nuitka',
            '--show-progress',
            '--show-memory',
            '--standalone',
            '--include-data-dir=src/icon=icon',
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
                        '--windows-icon-from-ico=src/icon/PDFeXpress.ico',
                        '--clang',
                        '--mingw64'
                        )
                )
    nuitka_cmd.append(f'src/{EXEC_NAME}.py')

    process = subprocess.run(nuitka_cmd, shell=True)
    if process.returncode != 0:
        raise ChildProcessError('nuitka building failed.')


def create_portable():
    if SYSTEM == 'Windows' and MACHINE == 'x86':
        win64_dir = f'{OUTPUT_DIR}/{EXEC_NAME}.dist/tkinterdnd2/tkdnd/win64'
        win64_dir = Path(win64_dir)
        if Path(win64_dir).exists():
            os.system(f'RD /S /Q {win64_dir}')

        src_win32_dir = Path('src/tkinterdnd2/tkdnd/win32')
        dist_win32_dir = Path(f'{OUTPUT_DIR}/{EXEC_NAME}.dist/tkinterdnd2/tkdnd/win32')
        if not dist_win32_dir.exists():
            dist_win32_dir.mkdir()
        os.system(f'COPY /Y {src_win32_dir}\\*.* {dist_win32_dir}')

    root_dir = f'{OUTPUT_DIR}/{EXEC_NAME}.dist'
    file_list = glob.glob(f'{root_dir}/**', recursive=True)
    file_list.sort()
    portable_file = f'{RELEASE_DIR}/{EXEC_NAME}-{APP_VERSION}-Portable-{SYSTEM}-{MACHINE}.zip'

    with ZipFile(portable_file, 'w', compression=ZIP_DEFLATED) as zf:
        for file in file_list:
            file = Path(file)
            if file.is_file():
                zf.write(file, f'{EXEC_NAME}-{MACHINE}/{"/".join(file.parts[3:])}')


def update_iss():
    settings = {
            'APP_VERSION': APP_VERSION,
            'PROJECT_DIR': str(PROJECT_DIR)
            }

    iss_src = f'{EXEC_NAME}-{MACHINE}.iss'
    iss_work = Path(BUILD_DIR) / iss_src

    with open(iss_src) as template:
        iss_script = template.read()

    for key in settings:
        iss_script = iss_script.replace(f'%%{key}%%', settings.get(key))

    with open(iss_work, 'w') as iss:
        iss.write(iss_script)

    return iss_work


def check_iss():
    if MACHINE == 'x64':
        program_files = os.environ.get('ProgramFiles(x86)')
    else:
        program_files = os.environ.get('ProgramFiles')
    iss_compiler = Path(program_files) / 'Inno Setup 6' / 'Compil32.exe'

    if iss_compiler.exists():
        return iss_compiler
    return None


def creat_setup():
    iss_work = update_iss()
    iss_compiler = check_iss()
    if iss_compiler:
        compiler_cmd = [str(iss_compiler), '/cc', str(iss_work)]
        process = subprocess.run(compiler_cmd)
        if process.returncode != 0:
            raise ChildProcessError('Creating Windows installer failed.')


if __name__ == '__main__':
    # print('Building...')
    # build()
    print('Creating portable package...', end='')
    create_portable()
    print('done.')
    if SYSTEM == 'Windows':
        print('Creating Windows Installer...', end='')
        creat_setup()
        print('Done')
