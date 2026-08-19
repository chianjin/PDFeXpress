import random
import tkinter as tk
from tkinter import ttk

from config import EXECUTABLE_PATH, PROJECT_VERSION
from util import settings
from util.helpers import get_title_font
from util.i18n import gettext_text as _

QR_DIR = EXECUTABLE_PATH / 'asset' / 'qrcode'


def _numeric_version(version: str) -> str:
    """返回版本号的数字部分（去掉 '-' 后的预发布/构建后缀）。

    如 '2.0-BETA' 与 '2.0' 视为同一版本，用于捐赠弹窗的「不再提示」判定。
    """
    return version.split('-', 1)[0].strip()


def maybe_show_donate(master) -> None:
    """自动提示逻辑（状态集中存于 settings.json）。

    - 已捐赠：永久隐藏。
    - 选过「不再提示」：版本号不变则隐藏；版本升级后一次性 20% 概率再弹。
    - 选过「以后再说」：每次启动 10% 概率再弹。
    - 首次安装（未做任何选择）：第 3 次启动弹出。
    """
    if settings.is_donated():
        return
    disabled_version = settings.donate_disabled_version()
    if disabled_version:
        if _numeric_version(disabled_version) != _numeric_version(PROJECT_VERSION):
            # 版本升级：记录新版本号，一次性触发 20% 概率，之后不再重复掷骰。
            settings.mark_donate_disabled(_numeric_version(PROJECT_VERSION))
            if random.random() < 0.20:
                DonateDialog(master)
        return
    if settings.is_donate_maybelater():
        if random.random() < 0.10:
            DonateDialog(master)
        return
    # 首次安装：第 3 次使用弹出。
    if settings.increment_usage() >= 3:
        DonateDialog(master)


def open_donate(master) -> None:
    """主动打开捐赠弹窗（如主界面「Support Me」按钮）。"""
    DonateDialog(master)


class DonateDialog(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title(_('Buy me a chicken leg'))
        self.resizable(False, False)
        self.transient(master)

        self._images: list[tk.PhotoImage] = []  # keep refs alive
        self._setup_ui()

        self._center_on_master()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self._on_later)
        self.wait_window(self)

    def _setup_ui(self):
        container = ttk.Frame(self, padding=(80, 50))
        container.pack(fill=tk.BOTH, expand=True)

        title_font = get_title_font()

        ttk.Label(
            container,
            text=_('Buy me a chicken leg') + ' 🍗',
            font=title_font,
            anchor='center',
        ).pack(fill=tk.X, pady=(0, 8))

        ttk.Label(
            container,
            text=_('If this tool has been helpful to you, feel free to buy me a chicken leg.'),
            anchor='center',
            wraplength=360,
        ).pack(fill=tk.X, pady=(0, 16))

        self._setup_qr_row(container)

        button_row = ttk.Frame(container)
        button_row.pack(fill=tk.X, pady=(16, 0))
        button_row.columnconfigure((0, 1, 2), weight=1, uniform='btn')

        ttk.Button(button_row, text=_('Supported'), command=self._on_supported).grid(
            row=0, column=0, padx=4, sticky='ew'
        )
        ttk.Button(button_row, text=_('Maybe Later'), command=self._on_later).grid(
            row=0, column=1, padx=4, sticky='ew'
        )
        ttk.Button(
            button_row,
            text=_("Don't Show Again"),
            command=self._on_never_again,
        ).grid(row=0, column=2, padx=4, sticky='ew')

    def _setup_qr_row(self, parent):
        qr_row = ttk.Frame(parent)
        qr_row.pack(fill=tk.X)
        qr_row.columnconfigure((0, 1), weight=1, uniform='qr')

        for column, (file_name, label) in enumerate(
            (
                ('wechat.png', _('WeChat')),
                ('alipay.png', _('Alipay')),
            )
        ):
            cell = ttk.Frame(qr_row)
            cell.grid(row=0, column=column, padx=10, sticky='n')
            self._place_qr(cell, file_name, label)

    def _place_qr(self, cell, file_name: str, label: str):
        path = QR_DIR / file_name
        try:
            if path.is_file():
                image = tk.PhotoImage(file=str(path))
                self._images.append(image)
                ttk.Label(cell, image=image).pack()
            else:
                ttk.Label(
                    cell,
                    text=_('QR code image not found'),
                    relief='solid',
                    borderwidth=1,
                    width=18,
                    anchor='center',
                ).pack(ipadx=10, ipady=30)
        except tk.TclError:
            ttk.Label(
                cell,
                text=_('QR code image not found'),
                relief='solid',
                borderwidth=1,
                width=18,
                anchor='center',
            ).pack(ipadx=10, ipady=30)
        ttk.Label(cell, text=label, anchor='center').pack(pady=(6, 0))

    def _on_supported(self):
        settings.mark_donated()
        self.destroy()

    def _on_never_again(self):
        settings.mark_donate_disabled(_numeric_version(PROJECT_VERSION))
        self.destroy()

    def _on_later(self):
        settings.mark_donate_maybelater()
        self.destroy()

    def _center_on_master(self):
        self.update_idletasks()
        master = self.master
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f'+{x}+{y}')
