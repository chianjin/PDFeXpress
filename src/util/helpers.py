import platform
import subprocess
import time
import tkinter as tk
from pathlib import Path
from tkinter.messagebox import askyesno

from config import HEADER_FONT_SIZE
from feature.feature_list import FEATURE_LIST
from util.i18n import gettext_text as _


def get_feature_info(feature_id: str) -> tuple[str, str]:
    for _category, features in FEATURE_LIST:
        for feature in features:
            if feature.feature_id == feature_id:
                return feature.display_name, feature.executive_text
    raise ValueError(f'Feature {feature_id} not found')


def get_title_font() -> tuple:
    from tkinter import font

    default_font = font.nametofont('TkDefaultFont')
    return default_font.actual('family'), HEADER_FONT_SIZE, 'bold'


def file_types_to_extensions(file_types) -> set[str]:
    return {
        ext.replace('*', '')
        for _, pattern in file_types
        if pattern != '*.*'
        for ext in (pattern if isinstance(pattern, tuple) else (pattern,))
    }


def filter_files(file_paths: list[Path], file_types) -> list[Path]:
    allowed_extensions = file_types_to_extensions(file_types)
    return [file for file in file_paths if file.suffix in allowed_extensions]


def filter_dropped_files(event: tk.Event, file_types, include_folders: bool = False):
    if not event.data:
        return []

    root = event.widget.winfo_toplevel()
    dropped_paths = [Path(path) for path in root.tk.splitlist(event.data)]

    file_paths = [path for path in dropped_paths if path.is_file()]

    if include_folders:
        for folder in (path for path in dropped_paths if path.is_dir()):
            file_paths.extend(folder.glob('*.*'))

    return filter_files(file_paths, file_types)


def enable_pdf_drop(widget: 'tk.Widget', variable: 'tk.StringVar', file_types=None) -> None:
    """Allow dragging a file onto *widget*; the first matching file path is
    written into *variable* (a tk.StringVar). Reuses filter_dropped_files so the
    same file-type rules apply as the Browse button."""
    from tkinterdnd2 import DND_FILES

    from util.file_types import FILE_TYPES

    target_types = file_types if file_types is not None else FILE_TYPES['PDF']

    def _on_drop(event):
        paths = filter_dropped_files(event, target_types, include_folders=False)
        if paths:
            variable.set(str(paths[0]))

    widget.drop_target_register(DND_FILES)
    widget.dnd_bind('<<Drop>>', _on_drop)


def filter_dropped_folders(event: tk.Event):
    if not event.data:
        return []
    root = event.widget.winfo_toplevel()
    dropped_paths = root.tk.splitlist(event.data)
    return [Path(path) for path in dropped_paths if Path(path).is_dir()]


def format_size(size: int, decimal_places: int = 1) -> str:
    if size <= 0:
        raise ValueError('文件大小不能小于等于0')

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    index = 0

    while size >= 1024 and index < len(units) - 1:
        size /= 1024.0
        index += 1

    if index == 0:
        return f'{int(size)} {units[index]}'

    return f'{size:.{decimal_places}f} {units[index]}'


def get_file_properties(file_path: Path) -> dict:
    stat = file_path.stat()

    size_str = format_size(stat.st_size)

    ctime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime))
    mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))

    return {
        '文件名': file_path.name,
        '文件夹': str(file_path.parent),
        '文件大小': size_str,
        '创建时间': ctime_str,
        '修改时间': mtime_str,
    }


def get_multiple_files_properties(file_paths: list[Path]) -> dict:
    return {
        '文件数': len(file_paths),
        '总大小': sum(file.stat().st_size for file in file_paths),
    }


def reveal_in_explorer(output_path):
    """用系统文件管理器打开文件夹，或定位到已生成的文件。
    Windows: 文件夹 -> `explorer "<folder>"`；文件 -> `explorer /select, "<file>"`。"""
    if not output_path:
        return
    path = Path(output_path)
    system = platform.system()
    if system == 'Windows':
        if path.is_file():
            subprocess.call(f'explorer /select, "{output_path}"', shell=False)
        elif path.is_dir():
            subprocess.call(f'explorer "{output_path}"', shell=False)
    elif system == 'Darwin':
        if path.is_file():
            subprocess.call(['open', '-R', str(path)], shell=False)
        else:
            subprocess.call(['open', str(path)], shell=False)
    else:
        target = path if path.exists() else path.parent
        subprocess.call(['xdg-open', str(target)], shell=False)


def prompt_open_output(master, output_path):
    """任务完成后询问是否查看生成的输出；选"是"则定位/打开该输出。"""
    if askyesno(
        parent=master,
        title=_('Done'),
        message=_('Task completed. View the generated file(s) now?'),
    ):
        reveal_in_explorer(output_path)
