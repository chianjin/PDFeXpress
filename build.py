import argparse
import os
import platform
import shutil
import subprocess
from pathlib import Path

from src.config import (
    EXECUTABLE_NAME,
    PROJECT_AUTHOR,
    PROJECT_NAME,
    PROJECT_URL,
    PROJECT_UUID,
    PROJECT_VERSION,
)

# Redefine paths for build script context
PROJECT_DIR = Path(__file__).parent.resolve()
SOURCE_DIR_NAME = 'src'
RELEASE_DIR_NAME = 'release'
BUILD_DIR_NAME = 'build'
DIST_DIR_NAME = 'dist'
ASSETS_DIR_NAME = 'asset'

RELEASE_DIR = Path(RELEASE_DIR_NAME) / PROJECT_VERSION

LATEST_VERSION_FILE = PROJECT_DIR / 'LATEST-VERSION'

PLATFORM = platform.system()
if PLATFORM == 'Darwin':
    PLATFORM = 'macOS'
MACHINE = platform.machine()

# Runtime resources (asset/locale) and feature modules are bundled into the
# PyInstaller build via --add-data / --collect-submodules below; they land in
# the frozen `_internal` directory that config.EXECUTIVE_PATH (sys._MEIPASS)
# resolves at runtime. No post-build copy of `data` is needed (src/data was
# removed).


DATA_FILES = (
    'LICENSE',
    'README.md',
    'README.zh_CN.md',
    'CHANGELOG.md',
    'CHANGELOG.zh_CN.md',
    'COPYRIGHT.md',
)

ARCHIVE_BASENAME = f'{PROJECT_NAME.replace(" ", "")}-Portable-{PLATFORM}-{MACHINE}-{PROJECT_VERSION}'
INSTALLER_BASENAME = f'{PROJECT_NAME.replace(" ", "")}-Setup-{PLATFORM}-{MACHINE}-{PROJECT_VERSION}'
SOURCE_BASENAME = f'{PROJECT_NAME.replace(" ", "")}-Source-{PROJECT_VERSION}'

ISS_TEMPLATE = f'{ASSETS_DIR_NAME}/{EXECUTABLE_NAME}.iss'
sep = ';' if PLATFORM == 'Windows' else ':'


def build_executable():
    """Build the executable using PyInstaller."""
    print('\n--- Building Executable ---')
    print('Building executable with PyInstaller...')

    # Path to the main script
    main_script = f'{SOURCE_DIR_NAME}/{EXECUTABLE_NAME}.py'

    command = ['pyinstaller', '--noconfirm', '--clean']
    command.extend(
        [
            '--windowed',
            f'--name={EXECUTABLE_NAME}',
            f'--distpath={DIST_DIR_NAME}',
            f'--workpath={BUILD_DIR_NAME}',
            f'--icon={SOURCE_DIR_NAME}/asset/icon/{EXECUTABLE_NAME}.ico',
            f'--add-data={SOURCE_DIR_NAME}/asset{sep}asset',
            f'--add-data={SOURCE_DIR_NAME}/locale{sep}locale',
            '--collect-submodules',
            'feature',
            main_script,
        ]
    )

    print(f'Running command: {" ".join(command)}')

    # 让 src 在 PyInstaller 启动时就进入模块搜索路径，否则
    # --collect-submodules feature 找不到 src/feature，打包后动态加载的
    # 功能（如“合并 PDF”）会全部显示“未实现”。
    env = os.environ.copy()
    src_path = str(PROJECT_DIR / SOURCE_DIR_NAME)
    env['PYTHONPATH'] = src_path + os.pathsep + env.get('PYTHONPATH', '')

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env,
        )
        print('Copying distribution files...')
        print(f'PyInstaller build successful: {PROJECT_DIR / DIST_DIR_NAME / EXECUTABLE_NAME}')

        for data_file in DATA_FILES:
            shutil.copy(data_file, f'{DIST_DIR_NAME}/{EXECUTABLE_NAME}')
        print('Executable build process completed.')
    except subprocess.CalledProcessError as e:
        print('PyInstaller build failed.')
        print(f'Stderr: {e.stderr}')
        print(f'Stdout: {e.stdout}')
        raise
    except FileNotFoundError:
        print(
            "Error: 'pyinstaller' command not found. Make sure PyInstaller is installed and in your PATH."
        )
        raise


def create_portable():
    """Create a portable zip archive of the built application."""
    print('\n--- Creating Portable Archive ---')
    print('Creating portable archive...')

    # Ensure the release directory exists
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    archive_basename = RELEASE_DIR / ARCHIVE_BASENAME

    # The directory to be zipped is inside DIST_DIR, named after the executive
    dist_dir = Path(f'{DIST_DIR_NAME}/{EXECUTABLE_NAME}')

    if not dist_dir.is_dir():
        print(f'Error: Source directory for archive not found: {dist_dir}')
        print('Please run the build_executive() function first.')
        return

    try:
        archive_path = shutil.make_archive(
            base_name=str(archive_basename), format='zip', root_dir=str(dist_dir)
        )
        print(f'Portable archive created successful: {archive_path}')
        print('Portable archive creation completed.')
    except Exception as e:
        print(f'Failed to create portable archive: {e}')
        raise


def create_source_archive():
    """Package the committed source via ``git archive`` into a zip.

    Only files already committed at HEAD are included; untracked and
    ignored files (build artifacts, caches, release packages) stay out.
    """
    print('\n--- Creating Source Archive ---')
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    archive_path = RELEASE_DIR / f'{SOURCE_BASENAME}.zip'
    command = ['git', 'archive', '--format=zip', '-o', str(archive_path), 'HEAD']
    print(f'Running: {" ".join(command)}')
    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=PROJECT_DIR,
        )
        print(f'Source archive created: {archive_path}')
        print('Source archive creation completed.')
    except subprocess.CalledProcessError as e:
        print(f'git archive failed: {e.stderr or e.stdout}')
        raise
    except FileNotFoundError:
        print("Error: 'git' command not found.")
        raise


def generate_iss():
    """Generate the Inno Setup script from the template."""
    if PLATFORM != 'Windows':
        print('Warning: Inno Setup is only supported on Windows.')
        return None

    print('Generating Inno Setup script...')

    with open(ISS_TEMPLATE, encoding='utf-8') as template:
        iss = template.read()

    iss = iss.replace('%%PROJECT_NAME%%', PROJECT_NAME)
    iss = iss.replace('%%PROJECT_VERSION%%', PROJECT_VERSION)
    iss = iss.replace('%%PROJECT_AUTHOR%%', PROJECT_AUTHOR)
    iss = iss.replace('%%PROJECT_URL%%', PROJECT_URL)
    iss = iss.replace('%%PROJECT_DIR%%', str(PROJECT_DIR))
    iss = iss.replace('%%INSTALL_DIR%%', PROJECT_NAME.replace(' ', ''))
    iss = iss.replace('%%EXECUTABLE_NAME%%', EXECUTABLE_NAME)
    iss = iss.replace('%%SETUP_BASENAME%%', str(INSTALLER_BASENAME))
    iss = iss.replace('%%PROJECT_UUID%%', PROJECT_UUID)

    setup_iss_file = f'{DIST_DIR_NAME}/{EXECUTABLE_NAME}.iss'
    with open(setup_iss_file, 'w', encoding='utf-8') as iss_file:
        iss_file.write(iss)

    print(f'Generated Inno Setup script at: {setup_iss_file}')
    return setup_iss_file


def chack_iscc():
    if PLATFORM != 'Windows':
        print('Warning: Inno Setup not supported on this platform.')
        return None

    # Detect both Inno Setup 6 and 7; the newer 7 is preferred when present
    program_dirs = [
        os.environ['ProgramFiles'],
        os.environ['ProgramFiles(x86)'],
    ]
    for version in ('6', '7'):
        for base in program_dirs:
            iscc_command = Path(base) / f'Inno Setup {version}/ISCC.exe'
            if iscc_command.exists():
                return iscc_command

    print('Warning: Inno Setup not found. Install Inno Setup 6 or 7 to create installer.')
    return None


def create_installer():
    """Create a Windows installer using Inno Setup."""
    if PLATFORM != 'Windows':
        print('Installer creation is only supported on Windows.')
        return

    print('\n--- Creating Installer ---')
    print('Creating Windows installer...')

    iss_script_path = generate_iss()
    if not iss_script_path:
        print('Failed to generate .iss script. Aborting installer creation.')
        return

    iscc_path = chack_iscc()
    if not iscc_path:
        print('Inno Setup compiler not found. Aborting installer creation.')
        return

    command = [str(iscc_path), '/Q', str(iss_script_path)]

    print(f'Running Inno Setup compiler: {" ".join(command)}')

    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print(
            f'Inno Setup build successful: '
            f'{PROJECT_DIR / RELEASE_DIR_NAME / PROJECT_VERSION / INSTALLER_BASENAME}.exe'
        )
        print('Installer creation process completed.')
    except subprocess.CalledProcessError as e:
        print('Inno Setup build failed.')
        print(f'Stderr: {e.stderr}')
        print(f'Stdout: {e.stdout}')
        raise
    except FileNotFoundError:
        print(f"Error: '{iscc_path}' not found.")
        raise


def write_latest_version():
    """Write the current version to LATEST-VERSION in the project root.

    The file lets the update-check mechanism learn the latest published
    version; its content is the bare PROJECT_VERSION string (with a
    trailing newline).
    """
    try:
        LATEST_VERSION_FILE.write_text(PROJECT_VERSION + '\n', encoding='utf-8')
        print(f'Updated {LATEST_VERSION_FILE.name}: {PROJECT_VERSION}')
    except OSError as e:
        print(f'Warning: failed to write {LATEST_VERSION_FILE.name}: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build script for {PROJECT_NAME}.')
    parser.add_argument(
        '-e',
        '--executable',
        action='store_true',
        help='Build the executable using PyInstaller.',
    )
    parser.add_argument('-p', '--portable', action='store_true', help='Create a portable zip archive.')
    parser.add_argument(
        '-s',
        '--source',
        action='store_true',
        help='Package the buildable source code into a zip archive.',
    )
    parser.add_argument(
        '-i',
        '--installer',
        action='store_true',
        help='Create a Windows installer (Windows only).',
    )

    args = parser.parse_args()

    if not any([args.executable, args.portable, args.installer, args.source]):
        print(f'\n--- Starting Full Build Process for {PROJECT_NAME} ---')
        create_source_archive()
        build_executable()
        create_portable()
        create_installer()
        write_latest_version()
        print(f'\n--- Full Build Process for {PROJECT_NAME} Completed ---')
    else:
        if args.executable:
            build_executable()
        if args.portable:
            create_portable()
        if args.installer:
            create_installer()
        if args.source:
            create_source_archive()

    print('\nBuild finished.')
