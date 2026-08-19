"""更新提示弹窗，及两个整合钩子。

- check_for_update(master)：启动后后台静默自检，仅在发现新版本且未被跳过时弹窗。
- open_update_check(master)：手动「检查更新」，有结果（含已是最新/失败）均反馈。

「跳过此版本」的持久化状态存于 util.settings（settings.json）。
"""
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from config import (
    BAIDU_DOWNLOAD_URL,
    PROJECT_NAME,
    PROJECT_VERSION,
    QUARK_DOWNLOAD_URL,
    UPDATE_RECHECK_DAYS,
)
from util.helpers import get_title_font
from util.i18n import gettext_text as _
from util import settings
from util.version_check import check_update


class UpdateDialog(tk.Toplevel):
    def __init__(self, master=None, latest_version: str = '', modal: bool = True):
        super().__init__(master)
        self.title(_('Update available'))
        self.resizable(False, False)
        self.transient(master)

        self._latest_version = latest_version
        self._setup_ui()

        self._center_on_master()
        # modal=True（手动「检查更新」）：独占焦点、阻塞直到关闭。
        # modal=False（启动后台自检）：非抢占、非模态，不打断正在进行的任务。
        if modal:
            self.grab_set()
            self.wait_window(self)

    def _setup_ui(self):
        container = ttk.Frame(self, padding=(50, 30))
        container.pack(fill=tk.BOTH, expand=True)

        title_font = get_title_font()

        ttk.Label(
            container,
            text=_('Update available'),
            font=title_font,
            anchor='center',
        ).pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            container,
            text=_('A new version of {} is available.').format(PROJECT_NAME),
            anchor='center',
        ).pack(fill=tk.X)

        ttk.Label(
            container,
            text=_('Current: {}    Latest: {}').format(
                PROJECT_VERSION, self._latest_version
            ),
            anchor='center',
        ).pack(fill=tk.X, pady=(4, 14))

        ttk.Label(
            container,
            text=_('Download the latest version from one of the cloud drives below:'),
            anchor='center',
            wraplength=380,
        ).pack(fill=tk.X, pady=(0, 14))

        download_row = ttk.Frame(container)
        download_row.pack(fill=tk.X)
        download_row.columnconfigure((0, 1), weight=1, uniform='dl')

        ttk.Button(
            download_row,
            text=_('Quark Netdisk'),
            command=lambda: webbrowser.open(QUARK_DOWNLOAD_URL, new=2),
        ).grid(row=0, column=0, padx=6, sticky='ew')
        ttk.Button(
            download_row,
            text=_('Baidu Netdisk'),
            command=lambda: webbrowser.open(BAIDU_DOWNLOAD_URL, new=2),
        ).grid(row=0, column=1, padx=6, sticky='ew')

        button_row = ttk.Frame(container)
        button_row.pack(fill=tk.X, pady=(14, 0))
        button_row.columnconfigure((0, 1), weight=1, uniform='btn')

        ttk.Button(
            button_row,
            text=_('Skip this version'),
            command=self._on_skip,
        ).grid(row=0, column=0, padx=6, sticky='ew')
        ttk.Button(
            button_row,
            text=_('Later'),
            command=self._on_later,
        ).grid(row=0, column=1, padx=6, sticky='ew')

    def _on_skip(self):
        settings.mark_update_skip(self._latest_version)
        self.destroy()

    def _on_later(self):
        settings.mark_update_later()
        self.destroy()

    def _center_on_master(self):
        self.update_idletasks()
        master = self.master
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f'+{x}+{y}')


def check_for_update(master) -> None:
    """启动后静默自检：后台请求，仅在有更新且未被跳过/未 snooze 时弹窗。

    自检弹窗为非模态（modal=False），不抢占焦点，不打断进行中的任务。
    「以后再说」后 UPDATE_RECHECK_DAYS 天内不再弹（仍照常检测，只是不打扰）。
    """
    def _run():
        result = check_update()
        if (
            result['status'] == 'update_available'
            and not settings.is_update_skipped(result['latest'])
            and not settings.is_update_snoozed(UPDATE_RECHECK_DAYS)
        ):
            master.after(0, lambda: UpdateDialog(master, result['latest'], modal=False))

    threading.Thread(target=_run, daemon=True).start()


def open_update_check(master) -> None:
    """手动「检查更新」：后台请求，结果（含已是最新/失败）均反馈给用户。"""
    def _run():
        result = check_update()
        status = result['status']
        if status == 'update_available' and not settings.is_update_skipped(result['latest']):
            master.after(0, lambda: UpdateDialog(master, result['latest']))
        elif status == 'up_to_date':
            master.after(
                0,
                lambda: messagebox.showinfo(
                    _('Up to date'),
                    _('Already the latest {} version.').format(PROJECT_VERSION),
                ),
            )
        else:
            master.after(
                0,
                lambda: messagebox.showwarning(
                    _('Check failed'),
                    _('Could not check for updates. Please try again later.'),
                ),
            )

    threading.Thread(target=_run, daemon=True).start()
