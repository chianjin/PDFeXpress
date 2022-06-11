import glob
import os
import platform
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from src.constants import APP_VERSION, EXEC_NAME

SYSTEM = platform.system()
ARCH = platform.architecture()[0][:2]

PROJECT_DIR = Path(__file__).absolute().parent
SOURCE_DIR = Path('src')
BUILD_DIR = Path('build')
RELEASE_DIR = Path('release') / APP_VERSION
OUTPUT_DIR = BUILD_DIR / f'{SYSTEM}-{ARCH}'


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
                        )
                )
    nuitka_cmd.append(SOURCE_DIR / f'{EXEC_NAME}.py')

    process = subprocess.run(nuitka_cmd, shell=True)
    if process.returncode != 0:
        raise ChildProcessError('Nuitka building failed.')

    # hack for win32
    if SYSTEM == 'Windows' and ARCH == '32':
        win64_dir = OUTPUT_DIR / f'{EXEC_NAME}.dist/tkinterdnd2/tkdnd/win64'
        if Path(win64_dir).exists():
            os.system(f'RD /S /Q {win64_dir}')

        src_dnd_dir = SOURCE_DIR / 'tkinterdnd2/tkdnd/win32'
        dist_dnd_dir = OUTPUT_DIR / f'{EXEC_NAME}.dist/tkinterdnd2/tkdnd/win32'
        if not dist_dnd_dir.exists():
            dist_dnd_dir.mkdir()
        os.system(f'COPY /Y {src_dnd_dir}\\*.* {dist_dnd_dir}')

    print('Building done.')


def create_portable():
    file_list = glob.glob(f'{OUTPUT_DIR / EXEC_NAME}.dist/**', recursive=True)
    file_list.sort()
    portable_file = RELEASE_DIR / f'{EXEC_NAME}-{APP_VERSION}-Portable-{SYSTEM}-{ARCH}.zip'

    print('Creating portable package...')
    with ZipFile(portable_file, 'w', compression=ZIP_DEFLATED) as zf:
        for file in file_list:
            file = Path(file)
            name_in_zip = f'{EXEC_NAME}-{ARCH}/{"/".join(file.parts[3:])}'
            print(name_in_zip)
            if file.is_file():
                zf.write(file, name_in_zip)
    print('Creating portable package done.')


def update_iss():
    settings = {
            'APP_VERSION': APP_VERSION,
            'PROJECT_DIR': str(PROJECT_DIR),
            'OUTPUT_DIR': str(OUTPUT_DIR),
            'RELEASE_DIR': str(RELEASE_DIR),
            'ARCH': ARCH,
            'ARCH_MODE': 'ArchitecturesInstallIn64BitMode=x64' if ARCH == '64' else ''
            }

    iss_template = f'{EXEC_NAME}-template.iss'
    iss_work = Path(BUILD_DIR) / f'{EXEC_NAME}-{ARCH}.iss'

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
    build()
    create_portable()
    if SYSTEM == 'Windows':
        create_setup()
