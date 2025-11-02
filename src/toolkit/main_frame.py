import tkinter as tk
from tkinter import ttk, messagebox

# Import i18n and feature modules
from config import PROJECT_NAME, PROJECT_VERSION, PROJECT_URL
from toolkit.i18n import gettext_text as _
from toolkit.ui.feature.delete_pages import DeletePagesApp
from toolkit.ui.feature.extract_image import ExtractImageApp
from toolkit.ui.feature.extract_text import ExtractTextApp
from toolkit.ui.feature.images_to_pdf import ImagesToPDFApp
from toolkit.ui.feature.interleave_pdf import InterleavePDFApp
from toolkit.ui.feature.merge_invoices import MergeInvoicesApp
from toolkit.ui.feature.edit_bookmark import EditBookmarkApp
from toolkit.ui.feature.merge_pdf import MergePDFApp
from toolkit.ui.feature.pdf_to_images import PDFToImagesApp
from toolkit.ui.feature.pdf_to_long_image import PDFToLongImageApp
from toolkit.ui.feature.rotate_pdf import RotatePDFApp
from toolkit.ui.feature.split_pdf import SplitPDFApp


class MainFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        # Main layout uses grid for fixed sidebar and expanding content
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Left Navigation Frame
        self.nav_frame = ttk.LabelFrame(self, text=_("Operation"))
        self.nav_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=5)
        self.nav_frame.columnconfigure(0, weight=1)

        # Bottom frame for About button
        about_frame = ttk.Frame(self.nav_frame)
        about_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)
        about_frame.columnconfigure(0, weight=1)

        # separator = ttk.Separator(about_frame)
        # separator.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        about_button = ttk.Button(about_frame, text=_("About"), command=self._show_about_dialog)
        about_button.grid(row=1, column=0, sticky="ew")

        # Top frame for navigation buttons
        top_nav_frame = ttk.Frame(self.nav_frame)
        top_nav_frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=5)
        top_nav_frame.columnconfigure(0, weight=1)

        self.current_app_frame = None
        self.app_instances = {}
        self.nav_buttons = {}

        # Navigation Buttons
        self._create_nav_button(top_nav_frame, _("Merge PDF"), MergePDFApp)
        self._create_nav_button(top_nav_frame, _("Interleave PDF"), InterleavePDFApp)
        self._create_nav_button(top_nav_frame, _("Split PDF"), SplitPDFApp)
        self._create_nav_button(top_nav_frame, _("Rotate PDF"), RotatePDFApp)
        self._create_nav_button(top_nav_frame, _("Extract Text"), ExtractTextApp)
        self._create_nav_button(top_nav_frame, _("Extract Image"), ExtractImageApp)
        self._create_nav_button(top_nav_frame, _("Images to PDF"), ImagesToPDFApp)
        self._create_nav_button(top_nav_frame, _("PDF to Images"), PDFToImagesApp)
        self._create_nav_button(top_nav_frame, _("PDF to Long Image"), PDFToLongImageApp)
        self._create_nav_button(top_nav_frame, _("Delete Pages"), DeletePagesApp)
        self._create_nav_button(top_nav_frame, _("Edit Bookmark"), EditBookmarkApp)
        self._create_nav_button(top_nav_frame, _("Merge Invoices"), MergeInvoicesApp)

        # Right Content Frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky="nswe")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Initially display the Merge PDF app
        self._show_app(MergePDFApp)

    def _create_nav_button(self, parent, text: str, app_class):
        button = ttk.Button(parent, text=text, command=lambda ac=app_class: self._show_app(ac))
        button.pack(fill='x', pady=(5, 0))
        self.nav_buttons[app_class] = button

    def _show_app(self, app_class):
        if app_class is None:
            messagebox.showinfo(_("Coming Soon"), _("Feature coming soon."))
            return

        if self.current_app_frame:
            self.current_app_frame.pack_forget()

        if app_class not in self.app_instances:
            self.app_instances[app_class] = app_class(self.content_frame)

        self.current_app_frame = self.app_instances[app_class]
        self.current_app_frame.pack(expand=True, fill="both")

        for ac, button in self.nav_buttons.items():
            if ac == app_class:
                button.state(['disabled'])
            else:
                button.state(['!disabled'])

    def _show_about_dialog(self):
        about_message = (
            f"{PROJECT_NAME} - {_('Ver.')} {PROJECT_VERSION}\n\n"
            f"{_('Project Home Page')}: {PROJECT_URL}\n\n"
            f"{_('Copyright © 2024 ChianJin. All rights reserved.')}"
        )
        messagebox.showinfo(
            _("About {}").format(PROJECT_NAME),
            about_message
        )


if __name__ == "__main__":
    import tkinterdnd2

    root = tkinterdnd2.Tk()
    root.title(_("PDF Toolbox Debug"))
    root.geometry("1080x600")
    app = MainFrame(root)
    root.mainloop()
