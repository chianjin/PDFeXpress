"""本地设置：把「支持我」与「更新检测」的持久化状态集中到一个 JSON 文件。

文件位置（与平台约定一致，用户可写、重装后仍保留）：
  Windows: %APPDATA%/PDFeXpress/settings.json
  macOS:   ~/Library/Application Support/PDFeXpress/settings.json
  Linux:   $XDG_DATA_HOME/PDFeXpress/settings.json（否则 ~/.local/share/PDFeXpress/settings.json）

字段：
  donated                  bool   是否已捐赠（永久隐藏捐赠弹窗）
  donate_disabled_version  str    选「不再提示」时记录的（数字）版本号，为空表示未选
  donate_maybelater       bool   是否选过「以后再说」
  usage_count             int    累计启动次数（首次安装第 3 次才弹捐赠）
  update_skip_version     str    选「跳过此版本」时记录的版本号，为空表示未跳过
  update_later_at        float  选「以后再说」时记录的时间戳（秒）；在窗口期内自检不弹窗
"""

import json
import os
import platform
import time
from pathlib import Path

SETTINGS_FILENAME = 'settings.json'

_DEFAULTS = {
    'donated': False,
    'donate_disabled_version': '',
    'donate_maybelater': False,
    'usage_count': 0,
    'update_skip_version': '',
    'update_later_at': 0.0,
}


def settings_dir() -> Path:
    system = platform.system()
    if system == 'Windows':
        base = os.environ.get('APPDATA')
        root = Path(base) if base else Path.home() / 'AppData' / 'Roaming'
    elif system == 'Darwin':
        root = Path.home() / 'Library' / 'Application Support'
    else:
        base = os.environ.get('XDG_DATA_HOME')
        root = Path(base) if base else Path.home() / '.local' / 'share'
    return root / 'PDFeXpress'


def settings_path() -> Path:
    return settings_dir() / SETTINGS_FILENAME


def _read_raw() -> dict:
    try:
        return json.loads(settings_path().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def _save(data: dict) -> None:
    """写入设置；best-effort，不抛异常。"""
    try:
        path = settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    except OSError:
        pass


def _load() -> dict:
    return {**_DEFAULTS, **_read_raw()}


# ---- 支持我（donate） ----
def is_donated() -> bool:
    return _load().get('donated', False)


def mark_donated() -> None:
    data = _load()
    data['donated'] = True
    _save(data)


def donate_disabled_version() -> str:
    return _load().get('donate_disabled_version', '')


def mark_donate_disabled(version: str) -> None:
    data = _load()
    data['donate_disabled_version'] = version
    data['donate_maybelater'] = False
    _save(data)


def is_donate_maybelater() -> bool:
    return _load().get('donate_maybelater', False)


def mark_donate_maybelater() -> None:
    data = _load()
    data['donate_maybelater'] = True
    data['donate_disabled_version'] = ''
    _save(data)


def clear_donate_dismiss() -> None:
    data = _load()
    data['donate_disabled_version'] = ''
    data['donate_maybelater'] = False
    _save(data)


def increment_usage() -> int:
    data = _load()
    data['usage_count'] = int(data.get('usage_count', 0)) + 1
    _save(data)
    return data['usage_count']


# ---- 更新检测（update） ----
def is_update_skipped(version: str) -> bool:
    return _load().get('update_skip_version', '') == version


def mark_update_skip(version: str) -> None:
    data = _load()
    data['update_skip_version'] = version
    _save(data)


def mark_update_later() -> None:
    """记录「以后再说」时间戳；窗口期内后台自检不弹更新框。"""
    data = _load()
    data['update_later_at'] = time.time()
    _save(data)


def is_update_snoozed(days: int) -> bool:
    """距上次「以后再说」是否还在 days 天的窗口期内（窗口内=True）。"""
    timestamp = _load().get('update_later_at', 0.0)
    if not timestamp:
        return False
    return (time.time() - timestamp) < days * 86400
