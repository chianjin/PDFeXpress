import tkinter as tk
from datetime import date
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from config import PROJECT_AUTHOR, PROJECT_NAME, PROJECT_URL, PROJECT_VERSION
from toolkit.i18n import gettext_text as _
from toolkit.third_packages import THIRD_PACKAGES
from toolkit.ui.feature.add_page_numbers import AddPageNumbers
from toolkit.ui.feature.delete_pages import DeletePagesApp
from toolkit.ui.feature.edit_bookmark import EditBookmarkApp
from toolkit.ui.feature.extract_images import ExtractImagesApp
from toolkit.ui.feature.extract_text import ExtractTextApp
from toolkit.ui.feature.images_to_pdf import ImagesToPDFApp
from toolkit.ui.feature.interleave_pdf import InterleavePDFApp
from toolkit.ui.feature.merge_invoices import MergeInvoicesApp
from toolkit.ui.feature.merge_pdf import MergePDFApp
from toolkit.ui.feature.pdf_to_images import PDFToImagesApp
from toolkit.ui.feature.pdf_to_long_image import PDFToLongImageApp
from toolkit.ui.feature.rotate_pdf import RotatePDFApp
from toolkit.ui.feature.split_pdf import SplitPDFApp
from toolkit.ui.widget.url import URLLabel


class MainFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill='both', expand=True)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.nav_frame = ttk.LabelFrame(self, text=_('Operation'))
        self.nav_frame.grid(row=0, column=0, sticky='ns', padx=(10, 0), pady=5)
        self.nav_frame.columnconfigure(0, weight=1)

        about_frame = ttk.Frame(self.nav_frame)
        about_frame.pack(side='bottom', fill='x', pady=5, padx=5)
        about_frame.columnconfigure(0, weight=1)

        about_button = ttk.Button(
            about_frame, text=_('About'), command=self._show_about_dialog
        )
        about_button.grid(row=1, column=0, sticky='ew')

        top_nav_frame = ttk.Frame(self.nav_frame)
        top_nav_frame.pack(side='top', fill='x', pady=5, padx=5)
        top_nav_frame.columnconfigure(0, weight=1)

        self.current_app_frame = None
        self.app_instances = {}
        self.nav_buttons = {}

        self._create_nav_button(top_nav_frame, _('Merge PDF'), MergePDFApp)
        self._create_nav_button(top_nav_frame, _('Split PDF'), SplitPDFApp)
        self._create_nav_button(top_nav_frame, _('Interleave PDF'), InterleavePDFApp)
        self._create_nav_button(top_nav_frame, _('Rotate PDF'), RotatePDFApp)
        self._create_nav_button(top_nav_frame, _('Extract Text'), ExtractTextApp)
        self._create_nav_button(top_nav_frame, _('Extract Images'), ExtractImagesApp)
        self._create_nav_button(top_nav_frame, _('Images to PDF'), ImagesToPDFApp)
        self._create_nav_button(top_nav_frame, _('PDF to Images'), PDFToImagesApp)
        self._create_nav_button(
            top_nav_frame, _('PDF to Long Image'), PDFToLongImageApp
        )

        self._create_nav_button(top_nav_frame, _('Delete Pages'), DeletePagesApp)
        self._create_nav_button(top_nav_frame, _('Add Page Numbers'), AddPageNumbers)
        self._create_nav_button(top_nav_frame, _('Edit Bookmark'), EditBookmarkApp)
        self._create_nav_button(top_nav_frame, _('Merge Invoices'), MergeInvoicesApp)

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky='nswe')
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        self._show_app(MergePDFApp)

    def _create_nav_button(self, parent, text: str, app_class):
        button = ttk.Button(
            parent,
            text=text,
            padding=(5, 0, 5, 0),
            command=lambda ac=app_class: self._show_app(ac),
            # style='Toolbutton',
        )
        button.pack(fill='x', pady=(5, 0))
        self.nav_buttons[app_class] = button

    def _show_app(self, app_class):
        if app_class is None:
            messagebox.showinfo(_('Coming Soon'), _('Feature coming soon.'))
            return

        if self.current_app_frame:
            self.current_app_frame.pack_forget()

        if app_class not in self.app_instances:
            self.app_instances[app_class] = app_class(self.content_frame)

        self.current_app_frame = self.app_instances[app_class]
        self.current_app_frame.pack(expand=True, fill='both')

        for ac, button in self.nav_buttons.items():
            if ac == app_class:
                button.state(['disabled'])
            else:
                button.state(['!disabled'])

    def _show_about_dialog(self):
        AboutFame(self)


class AboutFame(tk.Toplevel):
    def __init__(self, parent: ttk.Frame, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.grab_set()


        default_font = tkfont.nametofont('TkDefaultFont').actual()
        default_font_family = default_font['family']

        name_font = tkfont.Font(family=default_font_family, size=20, weight='bold')
        version_font = tkfont.Font(family=default_font_family, size=12, weight='bold')

        ttk.Label(self, text=PROJECT_NAME, font=name_font).grid(
            row=0, column=0, padx=10, pady=(20, 0)
        )
        ttk.Label(self, text=f'{_("Ver.")} {PROJECT_VERSION}', font=version_font).grid(
            row=1, column=0, padx=10, pady=(10, 0)
        )
        URLLabel(self, url=PROJECT_URL).grid(row=2, column=0, padx=10, pady=(10, 0))

        ttk.Label(
            self,
            text=_('Copyright © 2022-{} {}, All rights reserved.').format(
                date.today().year, PROJECT_AUTHOR
            ),
        ).grid(row=3, column=0, padx=40, pady=(10, 0))

        ttk.Label(self, text=_('------ The third software or packages -------')).grid(
            row=4, column=0, padx=10, pady=(20, 0)
        )

        third_packages_frame = ttk.Frame(self)
        third_packages_frame.grid(row=5, column=0, padx=40, pady=(0, 20))
        for row_index, (name, url, license_) in enumerate(THIRD_PACKAGES):
            URLLabel(third_packages_frame, text=name, url=url).grid(
                row=row_index, sticky='e', column=0, padx=10, pady=(5, 0)
            )
            ttk.Label(third_packages_frame, text=license_).grid(
                row=row_index, sticky='w', column=1, padx=10, pady=(5, 0)
            )

            ok_button = ttk.Button(self, text=_('OK'), command=lambda: self.destroy())
            ok_button.grid(row=6, column=0, padx=10, pady=(5, 20))

        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        self_width = self.winfo_width()
        self_height = self.winfo_height()

        x = parent_x + (parent_width - self_width) // 2
        y = parent_y + (parent_height - self_height) // 3

        self.geometry(f'+{x}+{y}')


if __name__ == '__main__':
    import tkinterdnd2

    root = tkinterdnd2.Tk()
    root.title(PROJECT_NAME)
    root.geometry('1080x600')
    app = MainFrame(root)
    root.mainloop()
