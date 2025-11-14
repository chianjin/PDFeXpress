import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from toolkit.core.add_page_numbers_worker import add_page_numbers_worker
from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.mixin import TaskRunnerMixin
from toolkit.ui.widget.file_picker import FilePicker
from toolkit.ui.widget.help_window import HelpWindow
from toolkit.ui.widget.misc import OptionFrame, TitleFrame
from toolkit.constant import HELP_ICON
from toolkit.util.help_contents import PAGE_NUMBERING_FORMAT
from toolkit.constant import FILE_TYPES_PDF


class AddPageNumbers(ttk.Frame, TaskRunnerMixin):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        TaskRunnerMixin.__init__(self, status_callback=self.update_status)
        self.help_window = None

        self.columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        TitleFrame(self, _('Add Page Numbers')).grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        self.input_file_picker = FilePicker(self, title=_('PDF File'), file_types=FILE_TYPES_PDF)
        self.input_file_picker.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

        self.output_file_picker = FilePicker(self, title=_('Output PDF'), file_types=FILE_TYPES_PDF, mode='save')
        self.output_file_picker.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 5))

        options_frame = OptionFrame(self, _('Options'))
        options_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))
        options_frame.columnconfigure(0, weight=1)


        rule_option = tk.Frame(options_frame)
        rule_option.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 5))

        ttk.Label(
            rule_option, text=_('Page Number Format:')
        ).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.rule_entry = ttk.Entry(rule_option)
        self.rule_entry.insert(0, "1-")
        self.rule_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.help_icon = tk.PhotoImage(file=HELP_ICON)
        ttk.Button(
            rule_option, text=_('Help'), command=self.show_help,
            style='Toolbutton', image=self.help_icon
        ).grid(row=0, column=2, sticky='w', padx=5, pady=0)
        ttk.Label(
            rule_option, text=_(PAGE_NUMBERING_FORMAT['brief']),
            wraplength= 600
        ).grid(row=0, column=3, sticky='w', padx=5, pady=5)

        pos_option = ttk.Frame(options_frame)
        pos_option.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        pos_option.columnconfigure(9, weight=1)

        self.v_pos = tk.StringVar(value='footer')
        self.h_pos = tk.StringVar(value='center')

        ttk.Label(
            pos_option, text=_('Position:')
        ).grid(row=0, column=0, sticky='w', padx=5, pady=5)

        ttk.Radiobutton(
            pos_option, text=_('Header'), variable=self.v_pos, value='header'
        ).grid(row=0, column=1, sticky='w', padx=5)
        ttk.Radiobutton(
            pos_option, text=_('Footer'), variable=self.v_pos, value='footer'
        ).grid(row=0, column=2, sticky='w', padx=5)

        ttk.Separator(
            pos_option, orient='vertical'
        ).grid(row=0, column=3, sticky='ns', padx=20)

        ttk.Radiobutton(
            pos_option, text=_('Left'), variable=self.h_pos, value='left'
        ).grid(row=0, column=4, sticky='w', padx=5)
        ttk.Radiobutton(
            pos_option, text=_('Center'), variable=self.h_pos, value='center'
        ).grid(row=0, column=5, sticky='w', padx=5)
        ttk.Radiobutton(
            pos_option, text=_('Right'), variable=self.h_pos, value='right'
        ).grid(row=0, column=6, sticky='w', padx=5)
        ttk.Radiobutton(
            pos_option, text=_('Outside'), variable=self.h_pos, value='outside'
        ).grid(row=0, column=7, sticky='w', padx=5)
        ttk.Radiobutton(
            pos_option, text=_('Inside'), variable=self.h_pos, value='inside'
        ).grid(row=0, column=8, sticky='w', padx=5)

        font_option = ttk.Frame(options_frame)
        font_option.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

        ttk.Label(
            font_option, text=_('Font:')
        ).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        supported_fonts = ["Courier", "Times", "Helvetica"]
        self.font_combo = ttk.Combobox(font_option, values=supported_fonts)
        self.font_combo.set("Times") # Default to Times
        self.font_combo.grid(row=0, column=1, sticky='ew', padx=5)

        ttk.Label(
            font_option, text=_('Style:')
        ).grid(row=0, column=2, sticky='w', padx=5)
        
        self.style_keys = ["Regular", "Bold", "Italic", "Bold Italic"]
        translated_styles = [_("Regular"), _("Bold"), _("Italic"), _("Bold Italic")]
        self.style_map = dict(zip(translated_styles, self.style_keys))

        self.font_style_combo = ttk.Combobox(font_option, values=translated_styles)
        self.font_style_combo.set(_("Regular")) # Default to Regular
        self.font_style_combo.grid(row=0, column=3, sticky='ew', padx=5)

        ttk.Label(
            font_option, text=_('Size:')
        ).grid(row=0, column=4, sticky='w', padx=5)
        self.font_size_spin = ttk.Spinbox(font_option, from_=6, to=72, increment=1)
        self.font_size_spin.set(10)
        self.font_size_spin.grid(row=0, column=5, sticky='ew', padx=5)

        margin_option = ttk.Frame(options_frame)
        margin_option.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))

        self.v_margin_label = ttk.Label(margin_option)
        self.v_margin_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.v_margin_spin = ttk.Spinbox(margin_option, from_=0, to=10, increment=0.1, format="%.1f")
        self.v_margin_spin.set(1.0)
        self.v_margin_spin.grid(row=0, column=1, sticky='w', padx=5)

        self.h_margin_label = ttk.Label(margin_option)
        self.h_margin_label.grid(row=0, column=2, sticky='w', padx=5)
        self.h_margin_spin = ttk.Spinbox(margin_option, from_=0, to=10, increment=0.1, format="%.1f")
        self.h_margin_spin.set(1.0)
        self.h_margin_spin.grid(row=0, column=3, sticky='ew', padx=5)
        self.v_pos.trace_add('write', self.update_margin_labels)
        self.h_pos.trace_add('write', self.update_margin_labels)
        self.update_margin_labels()


        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom_frame, text=_("Ready"), anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        self.run_button = ttk.Button(bottom_frame, text=_('Add'), command=self.run_task_from_ui)
        self.run_button.grid(row=0, column=1, padx=10, pady=5)

    def update_margin_labels(self, *args):
        if self.v_pos.get() == 'header':
            self.v_margin_label.config(text=_('Top Margin (cm):'))
        else:
            self.v_margin_label.config(text=_('Bottom Margin (cm):'))

        h_pos = self.h_pos.get()
        if h_pos == 'left':
            self.h_margin_label.config(text=_('Left Margin (cm):'))
            self.h_margin_label.grid(row=0, column=2, sticky='w', padx=5)
            self.h_margin_spin.grid(row=0, column=3, sticky='ew', padx=5)
            self.h_margin_spin.config(state='normal')
        elif h_pos == 'right':
            self.h_margin_label.config(text=_('Right Margin (cm):'))
            self.h_margin_label.grid(row=0, column=2, sticky='w', padx=5)
            self.h_margin_spin.grid(row=0, column=3, sticky='ew', padx=5)
            self.h_margin_spin.config(state='normal')
        elif h_pos in ('outside', 'inside'):
            self.h_margin_label.config(text=_('Edge Margin (cm):'))
            self.h_margin_label.grid(row=0, column=2, sticky='w', padx=5)
            self.h_margin_spin.grid(row=0, column=3, sticky='ew', padx=5)
            self.h_margin_spin.config(state='normal')
        else:
            self.h_margin_label.grid_forget()
            self.h_margin_spin.grid_forget()

    def show_help(self):
        if self.help_window is not None and self.help_window.winfo_exists():
            self.help_window.lift()
            return


        self.help_window = HelpWindow(
            self,
            title=PAGE_NUMBERING_FORMAT['title'],
            help_text= PAGE_NUMBERING_FORMAT['content'],
            on_close=self.on_help_window_close
        )

    def on_help_window_close(self):
        self.help_window = None

    def _get_root_window(self):
        return self.winfo_toplevel()

    def _prepare_task(self):
        input_path = self.input_file_picker.get()
        output_path = self.output_file_picker.get()
        rule = self.rule_entry.get()

        if not input_path:
            messagebox.showerror(_('Error'), _('Please select an input PDF file.'))
            return None

        if not output_path:
            messagebox.showerror(_('Error'), _('Please specify an output PDF file.'))
            return None

        if not rule:
            messagebox.showerror(_('Error'), _('Page number format rule cannot be empty.'))
            return None
        
        try:
            h_margin_val = 0.0
            if self.h_pos.get() != 'center':
                h_margin_val = float(self.h_margin_spin.get())

            selected_style = self.font_style_combo.get()
            english_style = self.style_map.get(selected_style, "Regular")

            args = (
                input_path,
                output_path,
                rule,
                self.v_pos.get(),
                self.h_pos.get(),
                self.font_combo.get(),
                english_style,
                int(self.font_size_spin.get()),
                float(self.v_margin_spin.get()),
                h_margin_val
            )
        except ValueError:
            messagebox.showerror(_('Error'), _('Please enter valid numbers for font size and margins.'))
            return None

        initial_label = _("Adding Page Numbers...")
        return add_page_numbers_worker, args, initial_label

    def update_status(self, message):
        self.status_label.config(text=message)