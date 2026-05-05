"""UI 工具模块"""

from pathlib import Path
import tkinter as tk
from typing import TYPE_CHECKING

from config import HEADER_FONT_SIZE

if TYPE_CHECKING:
    from .file_types import FILE_TYPES


def get_title_font() -> tuple:
    """获取标题字体配置（延迟初始化）

    Returns:
        字体元组: (字体系, 字号, 字重)
    """
    from tkinter import font

    default_font = font.nametofont('TkDefaultFont')
    return default_font.actual('family'), HEADER_FONT_SIZE, 'bold'


def file_types_to_extensions(file_types: FILE_TYPES) -> set[str]:
    """过滤文件列表，只保留指定扩展名的文件"""

    return {
        ext.replace('*', '')
        for _, pattern in file_types
        if pattern != '*.*'
        for ext in (pattern if isinstance(pattern, tuple) else (pattern,))
    }


def filter_files(file_paths: list[Path], file_types: FILE_TYPES) -> list[Path]:
    """过滤文件列表，只保留指定扩展名的文件"""

    allowed_extensions = file_types_to_extensions(file_types)
    return [file for file in file_paths if file.suffix in allowed_extensions]


def filter_dropped_files(event: tk.Event, file_types: FILE_TYPES, include_folders: bool = False):
    """
    处理拖拽的文件，排除目录并过滤扩展名

    Args:
        event: 拖拽事件
        file_types: 允许的扩展名列表，如 ['图像文件', ('*.png', '*.jpg')]
        include_folders: 包括文件夹内文件

    Returns:
        有效的文件路径列表
    """
    if not event.data:
        return []

    root = event.widget.winfo_toplevel()
    dropped_paths = root.tk.splitlist(event.data)

    file_paths = [Path(path) for path in dropped_paths if Path(path).is_file()]

    if include_folders:
        folder_paths = [Path(path) for path in dropped_paths if Path(path).is_dir()]
        for folder in folder_paths:
            file_paths.extend(folder.glob('*.*'))

    return filter_files(file_paths, file_types)


def filter_dropped_folders(event: tk.Event):
    """处理拖拽的文件夹

    Args:
        event: 拖拽事件

    Returns:
        有效的文件夹路径列表
    """
    if not event.data:
        return []
    root = event.widget.winfo_toplevel()
    dropped_paths = root.tk.splitlist(event.data)
    return [Path(path) for path in dropped_paths if Path(path).is_dir()]


def format_size(size: int, decimal_places: int = 1) -> str:
    """格式化文件大小"""

    if size <= 0:
        raise ValueError('文件大小不能小于等于0')

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    index = 0

    while size >= 1024 and index < len(units) - 1:
        size /= 1024.0
        index += 1

    # 对于整数 B，不显示小数
    if index == 0:
        return f'{int(size)} {units[index]}'

    # 其他单位保留指定小数位
    return f'{size:.{decimal_places}f} {units[index]}'


def get_file_properties(file_path: Path) -> dict:
    """获取文件属性（格式化后适合人类阅读）"""
    import time

    stat = file_path.stat()

    # 格式化文件大小
    size_str = format_size(stat.st_size)

    # 格式化时间
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
    return {'文件数': len(file_paths), '总小大': sum(file.stat().st_size for file in file_paths)}
