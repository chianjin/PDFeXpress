"""版本检测：读取远程 LATEST-VERSION，与本地版本比较。

逻辑层（UI 无关），可被启动自检或手动「检查更新」复用。
"""
import re
import urllib.request

from config import (
    BAIDU_DOWNLOAD_URL,
    LATEST_VERSION_URL,
    PROJECT_VERSION,
    QUARK_DOWNLOAD_URL,
)

DEFAULT_TIMEOUT = 5.0

# 合法版本形如 2.0 / 2.0.1 / v2.0-BETA，用于过滤远程返回的 HTML 错误页。
_VERSION_RE = re.compile(r'^\d+(\.\d+){0,2}(-[0-9A-Za-z.]+)?$')


def parse_version(version_string: str) -> tuple:
    """解析 '2.0' / '2.0.1' / 'v2.0-BETA' 为 (major, minor, patch, prerelease)。

    prerelease 为 '-' 之后的小写后缀；无后缀则为空串（视为正式版）。
    """
    raw = version_string.strip().lstrip('vV')
    main, _, prerelease = raw.partition('-')
    parts = [segment for segment in main.split('.') if segment != '']

    numbers = []
    for segment in parts[:3]:
        digits = ''
        for char in segment:
            if char.isdigit():
                digits += char
            else:
                break
        numbers.append(int(digits) if digits else 0)
    while len(numbers) < 3:
        numbers.append(0)

    return (numbers[0], numbers[1], numbers[2], prerelease.strip().lower())


def compare_versions(current: str, latest: str) -> int:
    """比较两版本。

    返回 -1 表示 latest 更新（需升级），0 表示一致，1 表示 current 更新。
    同号数值下：正式版（无后缀）优于预发布版（如 2.0 > 2.0-BETA）。
    """
    current_parts = parse_version(current)
    latest_parts = parse_version(latest)

    for index in range(3):
        if current_parts[index] != latest_parts[index]:
            return -1 if current_parts[index] < latest_parts[index] else 1

    # 数值相等，比较预发布后缀
    if current_parts[3] == latest_parts[3]:
        return 0
    if current_parts[3] == '':  # 当前为正式版，远程为预发布版 -> 当前更新
        return 1
    if latest_parts[3] == '':  # 远程为正式版，当前为预发布版 -> 需升级
        return -1
    # 同为预发布版，按字典序比较
    if current_parts[3] < latest_parts[3]:
        return -1
    if current_parts[3] > latest_parts[3]:
        return 1
    return 0


def fetch_latest_version(timeout: float = DEFAULT_TIMEOUT) -> str | None:
    """读取远程版本字符串（已清洗），任何失败返回 None。

    - 网络异常 / 超时 -> None
    - 远程返回 HTML 错误页（不匹配版本格式）-> None
    """
    try:
        request = urllib.request.Request(
            LATEST_VERSION_URL, headers={'User-Agent': 'PDFeXpress'}
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_text = response.read().decode('utf-8', errors='ignore')
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None

    for line in raw_text.splitlines():
        candidate = line.strip().lstrip('vV')
        if _VERSION_RE.match(candidate):
            return candidate
    return None


def check_update(
        current_version: str = PROJECT_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """执行一次检测，返回结构化结果。

    status 取值：
      'update_available'  远程更新
      'up_to_date'        已是最新（或本地为开发版高于远程）
      'error'             网络/解析失败，无法判断
    """
    latest = fetch_latest_version(timeout=timeout)
    if latest is None:
        return {
            'status': 'error',
            'current': current_version,
            'latest': None,
            'error': 'network',
        }

    status = 'update_available' if compare_versions(current_version, latest) < 0 else 'up_to_date'
    return {
        'status': status,
        'current': current_version,
        'latest': latest,
        'error': None,
    }
