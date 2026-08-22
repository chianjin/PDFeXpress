"""
file_manager.py
零依赖（纯标准库）跨平台文件管理器控制器。
支持平台：Windows / macOS / Linux
支持入参：str / pathlib.Path / os.PathLike
"""

import os
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from util.i18n import gettext_text as _

# 路径类型提示
PathType = str | Path | os.PathLike


class _BaseFileManager:
    """平台基类：统一预处理路径类型与校验"""
    def _normalize_path(self, path: PathType) -> str:
        """统一将 str / Path / PathLike 转换为绝对路径字符串"""
        return os.path.abspath(os.fspath(path))

    def open(self, folder_path: PathType):
        normalized = self._normalize_path(folder_path)
        if not os.path.isdir(normalized):
            raise NotADirectoryError(_(f"Folder not exist: {normalized}"))
        self._open_impl(normalized)

    def select(self, target_path: PathType):
        normalized = self._normalize_path(target_path)
        if not os.path.exists(normalized):
            raise FileNotFoundError(_(f"Path not exist: {normalized}"))
        self._select_impl(normalized)

    def _open_impl(self, folder_path: str):
        raise NotImplementedError

    def _select_impl(self, target_path: str):
        raise NotImplementedError


# =======================================================
# 1. Windows: 纯 ctypes + PowerShell COM (零依赖)
# =======================================================
class _WindowsFileManager(_BaseFileManager):
    def __init__(self):
        import ctypes
        from ctypes import wintypes

        self._ctypes = ctypes
        self._wintypes = wintypes
        self._hwnd = None

        self._user32 = ctypes.windll.user32
        self._ole32 = ctypes.windll.ole32
        self._ole32.CoInitialize(None)

        self._user32.IsWindow.argtypes = [wintypes.HWND]
        self._user32.IsWindow.restype = wintypes.BOOL
        self._user32.IsIconic.argtypes = [wintypes.HWND]
        self._user32.IsIconic.restype = wintypes.BOOL
        self._user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self._user32.ShowWindow.restype = wintypes.BOOL
        self._user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        self._user32.SetForegroundWindow.restype = wintypes.BOOL

    def _activate_window(self, hwnd):
        if hwnd and self._user32.IsWindow(hwnd):
            if self._user32.IsIconic(hwnd):
                self._user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            else:
                self._user32.ShowWindow(hwnd, 5)  # SW_SHOW
            self._user32.SetForegroundWindow(hwnd)

    def _get_explorer_hwnds(self):
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "(New-Object -ComObject Shell.Application).Windows() | "
            "Where-Object { $_.FullName -like '*explorer.exe' } | "
            "ForEach-Object { $_.HWND }"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=2, check=False)
            if res.returncode == 0 and res.stdout.strip():
                return set(int(h) for h in res.stdout.strip().splitlines() if h.strip().isdigit())
        except Exception:
            pass
        return set()

    def _open_impl(self, folder_path: str):
        escaped_path = folder_path.replace("'", "''")

        if self._hwnd and self._user32.IsWindow(self._hwnd):
            ps_script = f"""
            $shell = New-Object -ComObject Shell.Application
            $target = $shell.Windows() | Where-Object {{ $_.HWND -eq {self._hwnd} }}
            if ($target) {{ $target.Navigate2('{escaped_path}') }}
            """
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, check=False,
            )
            self._activate_window(self._hwnd)
            return

        prev_hwnds = self._get_explorer_hwnds()
        ps_open = f"""
        $shell = New-Object -ComObject Shell.Application
        $shell.Open('{escaped_path}')
        """
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_open], capture_output=True, check=False)

        for _i in range(15):
            time.sleep(0.1)
            current = self._get_explorer_hwnds()
            diff = current - prev_hwnds
            if diff:
                self._hwnd = diff.pop()
                self._activate_window(self._hwnd)
                break

    def _select_impl(self, target_path: str):
        parent_dir = os.path.dirname(target_path)
        item_name = os.path.basename(target_path)
        escaped_parent = parent_dir.replace("'", "''")
        escaped_item = item_name.replace("'", "''")

        if self._hwnd and self._user32.IsWindow(self._hwnd):
            ps_script = f"""
            $shell = New-Object -ComObject Shell.Application
            $win = $shell.Windows() | Where-Object {{ $_.HWND -eq {self._hwnd} }}
            if ($win) {{
                $win.Navigate2('{escaped_parent}')
                Start-Sleep -Milliseconds 250
                $folder = $shell.NameSpace('{escaped_parent}')
                $item = $folder.ParseName('{escaped_item}')
                if ($item) {{ $win.Document.SelectItem($item, 29) }}
            }}
            """
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, check=False,
            )
            self._activate_window(self._hwnd)
        else:
            shell32 = self._ctypes.windll.shell32
            ILCreateFromPathW = shell32.ILCreateFromPathW
            ILCreateFromPathW.argtypes = [self._wintypes.LPCWSTR]
            ILCreateFromPathW.restype = self._ctypes.c_void_p
            ILFree = shell32.ILFree
            ILFree.argtypes = [self._ctypes.c_void_p]

            prev_hwnds = self._get_explorer_hwnds()
            pidl = ILCreateFromPathW(target_path)
            if pidl:
                shell32.SHOpenFolderAndSelectItems(pidl, 0, None, 0)
                ILFree(pidl)

            for _i in range(15):
                time.sleep(0.1)
                current = self._get_explorer_hwnds()
                diff = current - prev_hwnds
                if diff:
                    self._hwnd = diff.pop()
                    break


# =======================================================
# 2. macOS: AppleScript / osascript (零依赖)
# =======================================================
class _MacOSFileManager(_BaseFileManager):
    def __init__(self):
        self.window_id = None

    def _run_applescript(self, script: str) -> str:
        proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
        return proc.stdout.strip()

    def _open_impl(self, folder_path: str):
        as_path = folder_path.replace('"', '\\"')
        if self.window_id:
            script = f'''
            tell application "Finder"
                activate
                try
                    set target_win to (first window whose id is {self.window_id})
                    set target of target_win to (POSIX file "{as_path}" as alias)
                    return {self.window_id}
                on error
                    set new_win to make new Finder window to (POSIX file "{as_path}" as alias)
                    return id of new_win
                end try
            end tell
            '''
        else:
            script = f'''
            tell application "Finder"
                activate
                set new_win to make new Finder window to (POSIX file "{as_path}" as alias)
                return id of new_win
            end tell
            '''

        res_id = self._run_applescript(script)
        if res_id:
            try:
                self.window_id = int(res_id)
            except ValueError:
                pass

    def _select_impl(self, target_path: str):
        as_path = target_path.replace('"', '\\"')
        script = f'''
        tell application "Finder"
            activate
            reveal (POSIX file "{as_path}" as alias)
            return id of front window
        end tell
        '''
        res_id = self._run_applescript(script)
        if res_id:
            try:
                self.window_id = int(res_id)
            except ValueError:
                pass


# =======================================================
# 3. Linux: FreeDesktop DBus / gdbus (零依赖)
# =======================================================
class _LinuxFileManager(_BaseFileManager):
    def _path_to_uri(self, path: str) -> str:
        return f"file://{quote(path)}"

    def _open_impl(self, folder_path: str):
        uri = self._path_to_uri(folder_path)
        cmd = [
            "gdbus", "call", "--session",
            "--dest", "org.freedesktop.FileManager1",
            "--object-path", "/org/freedesktop/FileManager1",
            "--method", "org.freedesktop.FileManager1.ShowFolders",
            f"['{uri}']", '""'
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=2, check=False)
            if res.returncode != 0:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception:
            subprocess.Popen(["xdg-open", folder_path])

    def _select_impl(self, target_path: str):
        uri = self._path_to_uri(target_path)
        cmd = [
            "gdbus", "call", "--session",
            "--dest", "org.freedesktop.FileManager1",
            "--object-path", "/org/freedesktop/FileManager1",
            "--method", "org.freedesktop.FileManager1.ShowItems",
            f"['{uri}']", '""'
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=2, check=False)
            if res.returncode != 0:
                parent_dir = os.path.dirname(target_path)
                subprocess.Popen(["xdg-open", parent_dir])
        except Exception:
            parent_dir = os.path.dirname(target_path)
            subprocess.Popen(["xdg-open", parent_dir])


# =======================================================
# 4. 对外工厂与统一接口
# =======================================================
def get_file_manager() -> _BaseFileManager:
    """自动获取当前操作系统对应的文件管理器实例"""
    if sys.platform.startswith("win"):
        return _WindowsFileManager()
    elif sys.platform == "darwin":
        return _MacOSFileManager()
    elif sys.platform.startswith("linux"):
        return _LinuxFileManager()
    else:
        raise OSError(f"暂不支持的系统: {sys.platform}")


@lru_cache(maxsize=1)
def _get_mgr():
    return get_file_manager()

def open_folder(folder_path: PathType):
    """跨平台打开目录（支持 str 与 pathlib.Path，自动复用窗口）"""
    _get_mgr().open(folder_path)

def select_file(target_path: PathType):
    """跨平台定位并高亮选中文件/目录（支持 str 与 pathlib.Path，自动复用窗口）"""
    _get_mgr().select(target_path)


# --------------------- 混合入参测试 ---------------------
if __name__ == "__main__":
    if sys.platform.startswith("win"):
        path_str = r"C:\Windows"
        path_obj = Path(r"C:\Windows\System32")
        file_obj = Path(r"C:\Windows\System32\cmd.exe")
    elif sys.platform == "darwin":
        path_str = "/Applications"
        path_obj = Path("/System/Library")
        file_obj = Path("/etc/hosts")
    else:
        path_str = os.path.expanduser("~")
        path_obj = Path("/usr/share")
        file_obj = Path("/etc/passwd")

    print("1. 使用 str 字符串路径打开...")
    open_folder(path_str)
    time.sleep(2)

    print("2. 使用 pathlib.Path 对象跳转目录（复用同一窗口）...")
    open_folder(path_obj)
    time.sleep(2)

    print("3. 使用 pathlib.Path 对象高亮定位文件（复用同一窗口）...")
    select_file(file_obj)
