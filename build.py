import os
import platform
import shutil
import subprocess
from pathlib import Path
import argparse

from config import (
    PROJECT_NAME, PROJECT_VERSION, EXECUTIVE_NAME, PROJECT_URL,
    PROJECT_AUTHOR, PROJECT_UUID
)

# Redefine paths for build script context
PROJECT_DIR = Path(__file__).parent.resolve()
SOURCE_DIR_NAME = "src"
RELEASE_DIR_NAME = "release"
BUILD_DIR_NAME = "build"
DIST_DIR_NAME = "dist"
ASSETS_DIR_NAME = "assets"

RELEASE_DIR = Path(RELEASE_DIR_NAME) / PROJECT_VERSION

PLATFORM = platform.system()
if PLATFORM == "Darwin": PLATFORM = "macOS"
MACHINE = platform.machine()

DATA_FOLDERS = (
        (f'{SOURCE_DIR_NAME}/locale', f'{DIST_DIR_NAME}/{EXECUTIVE_NAME}/locale'),
        (f'{SOURCE_DIR_NAME}/data', f'{DIST_DIR_NAME}/{EXECUTIVE_NAME}/data')
    )

DATA_FILES = (
        'LICENSE',
        'README.md', 'README.zh_CN.md',
        'CHANGELOG.md', 'CHANGELOG.zh_CN.md',
        'COPYRIGHT.md', 'COPYRIGHT.zh_CN.md'
    )


ARCHIVE_BASENAME = f"{PROJECT_NAME.replace(' ', '')}-Portable-{PLATFORM}-{MACHINE}-{PROJECT_VERSION}"
INSTALLER_BASENAME = f"{PROJECT_NAME.replace(' ', '')}-Setup-{PLATFORM}-{MACHINE}-{PROJECT_VERSION}"

ISS_TEMPLATE = f"{ASSETS_DIR_NAME}/{EXECUTIVE_NAME}.iss"
sep = ";" if PLATFORM == "Windows" else ":"

def build_executable():
    """Build the executable using PyInstaller."""
    print("\n--- Building Executable ---")
    print("Building executable with PyInstaller...")

    # Path to the main script
    main_script = f"{SOURCE_DIR_NAME}/{EXECUTIVE_NAME}.py"
    spec_file = f"{EXECUTIVE_NAME}.spec"

    command = ["pyinstaller", "--noconfirm", "--clean"]
    if Path(spec_file).exists():
        command.append(spec_file)
    else:
        command.extend([
            "--windowed",
            f"--name={EXECUTIVE_NAME}",
            f"--distpath={DIST_DIR_NAME}",
            f"--workpath={BUILD_DIR_NAME}",
            f"--icon=src/data/{EXECUTIVE_NAME}.ico",
            main_script,
        ])

    print(f"Running command: {' '.join(command)}")

    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print("Coping locale and data files...")
        print(f"PyInstaller build successful: {PROJECT_DIR / DIST_DIR_NAME / EXECUTIVE_NAME}")

        for data_file in DATA_FILES:
            shutil.copy(data_file, f'{DIST_DIR_NAME}/{EXECUTIVE_NAME}')
        for src_dir, dst_dir in DATA_FOLDERS:
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
        print("Executable build process completed.")
    except subprocess.CalledProcessError as e:
        print("PyInstaller build failed.")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        raise
    except FileNotFoundError:
        print("Error: 'pyinstaller' command not found. Make sure PyInstaller is installed and in your PATH.")
        raise


def create_portable():
    """Create a portable zip archive of the built application."""
    print("\n--- Creating Portable Archive ---")
    print("Creating portable archive...")

    # Ensure the release directory exists
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    archive_basename = RELEASE_DIR / ARCHIVE_BASENAME

    # The directory to be zipped is inside DIST_DIR, named after the executive
    dist_dir = Path(f'{DIST_DIR_NAME}/{EXECUTIVE_NAME}')

    if not dist_dir.is_dir():
        print(f"Error: Source directory for archive not found: {dist_dir}")
        print("Please run the build_executive() function first.")
        return

    try:
        archive_path = shutil.make_archive(
            base_name=str(archive_basename),
            format='zip',
            root_dir=str(dist_dir)
        )
        print(f"Portable archive created successful: {archive_path}")
        print("Portable archive creation completed.")
    except Exception as e:
        print(f"Failed to create portable archive: {e}")
        raise


def generate_iss():
    """Generate the Inno Setup script from the template."""
    if PLATFORM != "Windows":
        print("Warning: Inno Setup is only supported on Windows.")
        return None

    print("Generating Inno Setup script...")

    with open(ISS_TEMPLATE, 'r', encoding='utf-8') as template:
        iss = template.read()

    iss = iss.replace("%%PROJECT_NAME%%", PROJECT_NAME)
    iss = iss.replace("%%PROJECT_VERSION%%", PROJECT_VERSION)
    iss = iss.replace("%%PROJECT_AUTHOR%%", PROJECT_AUTHOR)
    iss = iss.replace("%%PROJECT_URL%%", PROJECT_URL)
    iss = iss.replace("%%PROJECT_DIR%%", str(PROJECT_DIR))
    iss = iss.replace("%%EXECUTIVE_NAME%%", EXECUTIVE_NAME)
    iss = iss.replace("%%SETUP_BASENAME%%", str(INSTALLER_BASENAME))
    iss = iss.replace("%%PROJECT_UUID%%", PROJECT_UUID)

    setup_iss_file = f'{DIST_DIR_NAME}/{EXECUTIVE_NAME}.iss'
    with open(setup_iss_file, 'w', encoding='utf-8') as iss_file:
        iss_file.write(iss)

    print(f"Generated Inno Setup script at: {setup_iss_file}")
    return setup_iss_file


def chack_iscc():
    if PLATFORM != "Windows":
        print("Warning: Inno Setup not supported on this platform.")
        return None

    iscc_command = Path(os.environ["ProgramFiles(x86)"]) / "Inno Setup 6/ISCC.exe"
    if iscc_command.exists():
        return iscc_command

    iscc_command = Path(os.environ["ProgramFiles"]) / "Inno Setup 6/ISCC.exe"
    if iscc_command.exists():
        return iscc_command

    print("Warning: Inno Setup not found. Install Inno Setup 6 to create installer.")
    return None


def create_installer():
    """Create a Windows installer using Inno Setup."""
    if PLATFORM != "Windows":
        print("Installer creation is only supported on Windows.")
        return

    print("\n--- Creating Installer ---")
    print("Creating Windows installer...")

    iss_script_path = generate_iss()
    if not iss_script_path:
        print("Failed to generate .iss script. Aborting installer creation.")
        return

    iscc_path = chack_iscc()
    if not iscc_path:
        print("Inno Setup compiler not found. Aborting installer creation.")
        return

    command = [str(iscc_path), '/Q', str(iss_script_path)]

    print(f"Running Inno Setup compiler: {' '.join(command)}")

    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print(f"Inno Setup build successful: {PROJECT_DIR/ RELEASE_DIR_NAME / PROJECT_VERSION / INSTALLER_BASENAME}.exe")
        print("Installer creation process completed.")
    except subprocess.CalledProcessError as e:
        print("Inno Setup build failed.")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        raise
    except FileNotFoundError:
        print(f"Error: '{iscc_path}' not found.")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build script for {PROJECT_NAME}.")
    parser.add_argument("-e", "--executable", action="store_true", help="Build the executable using PyInstaller.")
    parser.add_argument("-p", "--portable", action="store_true", help="Create a portable zip archive.")
    parser.add_argument("-i", "--installer", action="store_true", help="Create a Windows installer (Windows only).")

    args = parser.parse_args()

    if not any([args.executable, args.portable, args.installer]):
        print(f"\n--- Starting Full Build Process for {PROJECT_NAME} ---")
        build_executable()
        create_portable()
        create_installer()
        print(f"\n--- Full Build Process for {PROJECT_NAME} Completed ---")
    else:
        if args.executable:
            build_executable()
        if args.portable:
            create_portable()
        if args.installer:
            create_installer()

    print("\nBuild script finished.")
