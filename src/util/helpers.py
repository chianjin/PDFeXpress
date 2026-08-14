import time
from pathlib import Path
import tkinter as tk

from config import HEADER_FONT_SIZE
from feature.feature_list import FEATURE_LIST


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
    return {'文件数': len(file_paths), '总大小': sum(file.stat().st_size for file in file_paths)}
