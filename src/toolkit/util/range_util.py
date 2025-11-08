"""
范围解析工具模块
提供通用的页面范围解析功能，用于PDF处理操作
"""
from typing import List
from toolkit.i18n import gettext_text as _


def _parse_range(range_string: str, total_pages: int) -> List[int]:
    """解析单个范围表达: 1-9:3"""
    chunk: List[int] = []

    # 处理步长语法 (例如: 1-10:3 或 :3)
    step = 1
    range_part = range_string
    
    if ':' in range_string:
        # 使用rsplit确保支持负数范围（如:-10:3）
        range_part, step_part = range_string.rsplit(':', 1)
        step = int(step_part)
        
        # 检查特殊形式 :3 (全局范围)
        if range_part == '':
            # 全局范围：从首页到最后一页
            return list(range(0, total_pages, step))
    
    # 现在解析范围部分（可能之前有冒号部分已被分离）
    if '-' in range_part:
        # 检查是否是省略范围
        if range_part.startswith('-') and range_part.count('-') == 1:
            # 格式 '-10': 从第1页到第10页
            start = 1
            end = int(range_part[1:])
        elif range_part.endswith('-') and range_part.count('-') == 1:
            # 格式 '5-': 从第5页到最后
            start = int(range_part[:-1])
            end = total_pages
        else:
            # 标准格式 '1-10' 或 '1-10:3'（其中:3已被处理）
            start_str, end_str = range_part.split('-', 1)
            start = int(start_str)
            end = int(end_str)
            
            # 检查反向范围
            if start > end:
                # 反向范围，需要反向生成页码列表，负步长
                return list(range(start - 1, end - 2, -step))
        
        if start < 1 or end > total_pages:
            raise ValueError(
                _(
                    "Invalid range '{part}': must be between 1-{total_pages}."
                ).format(part=range_string, total_pages=total_pages)
            )

        # 生成指定步长的页码列表
        chunk = list(range(start - 1, end, step))
    else:
        # 单个页码
        page = int(range_part)
        if page < 1 or page > total_pages:
            raise ValueError(
                _(
                    "Invalid page '{part}': must be between 1-{total_pages}."
                ).format(part=range_string, total_pages=total_pages)
            )
        chunk = [page - 1]
    
    return chunk


def _parse_ranges_without_duplicates(range_string: str, total_pages: int) -> List[int]:
    """解析范围组: 3,1-6,10-:2"""
    chunk: List[int] = []
    seen = set()
    
    for range_part in range_string.split(","):
        range_part = range_part.strip()
        if not range_part:
            continue
            
        range_pages = _parse_range(range_part, total_pages)
        
        for page in range_pages:
            if page not in seen:
                seen.add(page)
                chunk.append(page)
    
    return chunk


def _parse_ranges_with_duplicates(range_string: str, total_pages: int) -> List[int]:
    """解析允许重复范围组: +9,12-5,7,12-:3"""
    chunk: List[int] = []
    
    # 去掉可能的+前缀
    if range_string.startswith('+'):
        range_string = range_string[1:].strip()
    
    for range_part in range_string.split(","):
        range_part = range_part.strip()
        if not range_part:
            continue
            
        chunk.extend(_parse_range(range_part, total_pages))
    
    return chunk


def parse_page_ranges(
    range_string: str,
    total_pages: int,
    allow_duplicates: bool = True
) -> List[List[int]]:
    chunks: List[List[int]] = []

    for range_group in range_string.split(";"):
        range_group = range_group.strip()
        if not range_group:
            continue

        if range_group.startswith("+"):
            # 以+开头的组，只在允许重复模式下调用
            if allow_duplicates:
                chunks.append(_parse_ranges_with_duplicates(range_group, total_pages))
            else:
                raise ValueError(_("Duplicates are not allowed"))
        else:
            # 不以+开头的组
            chunks.append(_parse_ranges_without_duplicates(range_group, total_pages))

    return chunks