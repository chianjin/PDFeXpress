import os
import platform
import random
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from config import EXECUTABLE_PATH, PROJECT_VERSION
from util.helpers import get_title_font
from util.i18n import gettext_text as _

QR_DIR = EXECUTABLE_PATH / 'asset' / 'qrcode'


def _flag_dir() -> Path:
    """User-writable dir for donate flags, following platform conventions.

    - Windows: %APPDATA%/PDFeXpress
    - macOS:   ~/Library/Application Support/PDFeXpress
    - Linux:   $XDG_DATA_HOME/PDFeXpress, else ~/.local/share/PDFeXpress
    """
    system = platform.system()
    if system == 'Windows':
        base = os.environ.get('APPDATA')
        root = Path(base) if base else Path.home() / 'AppData' / 'Roaming'
    elif system == 'Darwin':
        root = Path.home() / 'Library' / 'Application Support'
    else:  # Linux and other POSIX
        base = os.environ.get('XDG_DATA_HOME')
        root = Path(base) if base else Path.home() / '.local' / 'share'
    return root / 'PDFeXpress'


def _donated_path() -> Path:
    return _flag_dir() / 'donate.donated'


def _disabled_path() -> Path:
    return _flag_dir() / 'donate.disabled'


def _is_donated() -> bool:
    """True once the user has donated — permanently suppressed.

    The donated flag survives reinstall and upgrade, so the dialog stays
    hidden even after a fresh install.
    """
    try:
        return _donated_path().exists()
    except OSError:
        return False


def _numeric_version(version: str) -> str:
    """Return the bare numeric part of a version string.

    Strips any pre-release/build suffix after a '-', so '2.0-BETA' and
    '2.0' are treated as the same version for detection purposes.
    """
    return version.split('-', 1)[0].strip()


def _disabled_version() -> str | None:
    """Return the app version stored when 'don't show again' was chosen.

    None if the flag file is missing or unreadable.
    """
    try:
        return _disabled_path().read_text(encoding='utf-8').strip()
    except (OSError, ValueError):
        return None


def _mark_donated() -> None:
    """Record donation. Best-effort: never raises."""
    try:
        _donated_path().parent.mkdir(parents=True, exist_ok=True)
        _donated_path().touch()
    except OSError:
        pass


def _clear_dismiss_modes() -> None:
    """Remove any 'don't show again' / 'maybe later' flag files.

    Only one dismissal mode is active at a time, so switching modes must
    clear the previous one. The donated flag is left untouched (permanent).
    """
    for path in (_disabled_path(), _maybelater_path()):
        try:
            path.unlink()
        except OSError:
            pass


def _mark_disabled() -> None:
    """Record 'don't show again' with the current numeric app version.

    Only the numeric part (before any '-' suffix) is stored, so
    '2.0-BETA' and '2.0' count as the same version. While that version
    stays the same the dialog stays hidden. On a later upgrade (different
    numeric version) a one-time 20% chance reopens it. Best-effort.
    """
    try:
        _clear_dismiss_modes()
        path = _disabled_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_numeric_version(PROJECT_VERSION), encoding='utf-8')
    except OSError:
        pass


def _mark_maybelater() -> None:
    """Record 'maybe later' so the dialog reopens at 10% per launch."""
    try:
        _clear_dismiss_modes()
        path = _maybelater_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    except OSError:
        pass


def _is_maybelater() -> bool:
    try:
        return _maybelater_path().exists()
    except OSError:
        return False


def _maybelater_path() -> Path:
    return _flag_dir() / 'donate.maybelater'


def _usage_path() -> Path:
    return _flag_dir() / 'donate.usage'


def _increment_usage() -> int:
    """Increment and persist the launch counter; return the new count.

    Only consulted on first install, before any dismissal choice is made.
    """
    try:
        path = _usage_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            n = int(path.read_text(encoding='utf-8').strip() or '0')
        except (OSError, ValueError):
            n = 0
        n += 1
        path.write_text(str(n), encoding='utf-8')
        return n
    except OSError:
        return 1


def maybe_show_donate(master) -> None:
    """Auto-prompt logic for the donate dialog.

    - Donated: never show again.
    - 'Don't show again': hidden until the app version changes, then a
      one-time 20% chance per version bump.
    - 'Maybe later': 10% chance on each launch.
    - First install (no choice yet): show on the 3rd launch.
    """
    if _is_donated():
        return
    disabled = _disabled_path()
    if disabled.exists():
        stored = _disabled_version()
        if stored is None or _numeric_version(stored) != _numeric_version(PROJECT_VERSION):
            # Version changed: one-time 20% chance, then consume the trigger
            # so it does not re-roll on every launch in the new version.
            _mark_disabled()
            if random.random() < 0.20:
                DonateDialog(master)
        return
    if _is_maybelater():
        if random.random() < 0.10:
            DonateDialog(master)
        return
    # First install: pop on the 3rd use.
    if _increment_usage() >= 3:
        DonateDialog(master)


def open_donate(master) -> None:
    """Open the donate dialog on demand (e.g. the main 'Support' button)."""
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
            text=_(
                'If this tool has been helpful to you, feel free to '
                'buy me a chicken leg.'
            ),
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
        _mark_donated()
        self.destroy()

    def _on_never_again(self):
        _mark_disabled()
        self.destroy()

    def _on_later(self):
        _mark_maybelater()
        self.destroy()

    def _center_on_master(self):
        self.update_idletasks()
        master = self.master
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f'+{x}+{y}')
