import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilenames

from tkinterdnd2 import DND_FILES

from util.file_types import FILE_TYPES
from util.helpers import filter_dropped_files, filter_files
from util.i18n import gettext_text as _


class FileListView(tk.Frame):
    def __init__(
        self,
        master,
        trace_variable: tk.StringVar | None = None,
        file_types=FILE_TYPES['PDF'],
        sortable: bool = True,
        allow_duplicates: bool = True,
        **kw,
    ):
        super().__init__(master)

        self._file_types = file_types
        self._sortable = sortable
        self._allow_duplicates = allow_duplicates
        self._sort_state = 'unknown'  # 'unknown', 'ascending' 'descending'
        self._first_file = trace_variable

        self._setup_ui()

    def _setup_ui(self):

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._create_treeview()
        self._create_buttons()
        self._create_context_menu()
        self._setup_drag_drop()

    def _create_treeview(self):
        self.filelist_treeview = ttk.Treeview(
            self,
            columns=('fullpath', 'filename'),
            show='headings',
            selectmode='extended',
        )
        header_text = _('File Name') if not self._sortable else _('File Name ❓')
        if self._sortable:
            self.filelist_treeview.heading(
                'filename', text=header_text, command=self._sort_filelist, anchor='w'
            )
        else:
            self.filelist_treeview.heading('filename', text=header_text, anchor='w')

        self.filelist_treeview.column('filename', anchor='w')
        self.filelist_treeview.column('fullpath', width=0, stretch=False, minwidth=0)

        self.filelist_treeview.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(
            self, orient='vertical', command=self.filelist_treeview.yview
        )
        self.filelist_treeview.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def _create_buttons(self):

        buttons = [
            (_('Add Files'), self._add_files),
            (_('Add Folder'), self._add_folder),
            (_('Remove Selected'), self._remove_selected),
            (_('Remove All'), self._remove_all),
        ]

        if self._sortable:
            buttons.append(('separator', None))
            buttons.extend(
                [
                    (_('Move to Top'), self._move_to_first),
                    (_('Move Up'), self._move_up),
                    (_('Move Down'), self._move_down),
                    (_('Move to Last'), self._move_to_last),
                ]
            )

        button_frame = tk.Frame(self)
        for text, command in buttons:
            if text == 'separator':
                ttk.Separator(button_frame, orient=tk.HORIZONTAL).pack(
                    fill=tk.X, pady=(2, 7)
                )
            else:
                ttk.Button(button_frame, text=text, command=command).pack(
                    fill=tk.X, pady=(0, 5)
                )
        button_frame.grid(row=0, column=2, sticky='nsew', padx=(5, 0))

    def _show_context_menu(self, event) -> None:
        self._context_menu.post(event.x_root, event.y_root)

    def _create_context_menu(self) -> None:
        self._context_menu = tk.Menu(self.filelist_treeview, tearoff=0)
        self._context_menu.add_command(label=_('Select All'), command=self._select_all)
        self._context_menu.add_command(
            label=_('Invert Selection'), command=self._invert_selection
        )
        self._context_menu.add_command(
            label=_('Clear Selection'), command=self._clear_selection
        )

        self.filelist_treeview.bind('<Button-3>', self._show_context_menu)

    def _select_all(self):
        all_items = self.filelist_treeview.get_children()
        self.filelist_treeview.selection_set(all_items)

    def _invert_selection(self):
        all_items = self.filelist_treeview.get_children()
        selected = self.filelist_treeview.selection()
        for item in all_items:
            if item in selected:
                self.filelist_treeview.selection_remove(item)
            else:
                self.filelist_treeview.selection_add(item)

    def _clear_selection(self):
        all_items = self.filelist_treeview.get_children()
        self.filelist_treeview.selection_remove(all_items)

    def _setup_drag_drop(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event):
        paths = filter_dropped_files(event, self._file_types, include_folders=True)
        if not paths:
            return
        self._add_files_to_treeview(paths)

    def _update_header_text(self):
        if not self._sortable:
            return

        state_icons = {
            'unknown': '❓',
            'ascending': '⬆️',
            'descending': '⬇️',
        }
        icon = state_icons.get(self._sort_state, '❓')
        self.filelist_treeview.heading(
            'filename', text=_('File Name {icon}').format(icon=icon)
        )

    def _sort_filelist(self):
        if not self._sortable:
            return

        total_items = len(self.filelist_treeview.get_children())
        if total_items < 2:
            return

        if self._sort_state in ('unknown', 'descending'):
            new_state = 'ascending'
            reverse = False
        else:  # ascending
            new_state = 'descending'
            reverse = True

        items = []
        for item_id in self.filelist_treeview.get_children():
            values = self.filelist_treeview.item(item_id, 'values')
            filename = values[1] if len(values) > 1 else values[0]
            items.append((item_id, filename))

        items.sort(key=lambda x: x[1].lower(), reverse=reverse)

        for item_id, _name in items:
            self.filelist_treeview.move(item_id, '', tk.END)

        self._sort_state = new_state
        self._update_header_text()

    def _reset_sort_state(self):
        if self._sortable and self._sort_state != 'unknown':
            self._sort_state = 'unknown'
            self._update_header_text()

    def _get_existing_file_paths(self):
        file_paths = []
        for item_id in self.filelist_treeview.get_children():
            fullpath, _ = self.filelist_treeview.item(item_id, 'values')
            file_paths.append(fullpath)
        return file_paths

    def _add_files_to_treeview(self, file_paths):
        _changed = False

        if not self._allow_duplicates:
            existing_paths = set(self._get_existing_file_paths())

        for file_path in file_paths:
            if not self._allow_duplicates and str(file_path) in existing_paths:
                continue

            self.filelist_treeview.insert(
                '', tk.END, values=(str(file_path), file_path.name)
            )
            _changed = True

            if not self._allow_duplicates:
                existing_paths.add(str(file_path))

        if _changed:
            self._reset_sort_state()

    def _add_files(self):
        file_paths = askopenfilenames(
            filetypes=self._file_types,
        )
        if not file_paths:
            return
        self._add_files_to_treeview([Path(file_path) for file_path in file_paths])

    def _add_folder(self):
        folder = askdirectory()
        if not folder:
            return
        file_paths = filter_files(Path(folder).glob('*.*'), self._file_types)
        self._add_files_to_treeview(file_paths)

    def _remove_selected(self):
        selected = self.filelist_treeview.selection()
        for item in selected[::-1]:
            self.filelist_treeview.delete(item)
        if len(self.filelist_treeview.get_children()) < 2:
            self._reset_sort_state()

    def _remove_all(self):
        all_items = self.filelist_treeview.get_children()
        for item in all_items[::-1]:
            self.filelist_treeview.delete(item)
        self._reset_sort_state()

    def _move_to_first(self):
        selected = self.filelist_treeview.selection()
        if not selected:
            return
        for item in selected[::-1]:
            index = self.filelist_treeview.index(item)
            if index == 0:
                continue
            self.filelist_treeview.move(item, '', 0)
        self._reset_sort_state()

    def _move_up(self):
        selected = self.filelist_treeview.selection()
        if not selected:
            return
        for item in selected:
            index = self.filelist_treeview.index(item)
            if index == 0:
                continue
            self.filelist_treeview.move(item, '', index - 1)
        self._reset_sort_state()

    def _move_down(self):
        selected = self.filelist_treeview.selection()
        if not selected:
            return
        total_items = len(self.filelist_treeview.get_children())
        for item in selected[::-1]:
            index = self.filelist_treeview.index(item)
            if index == total_items - 1:
                continue
            self.filelist_treeview.move(item, '', index + 1)
        self._reset_sort_state()

    def _move_to_last(self):
        selected = self.filelist_treeview.selection()
        if not selected:
            return
        total_items = len(self.filelist_treeview.get_children())
        for item in selected:
            self.filelist_treeview.move(item, '', total_items - 1)
        self._reset_sort_state()

    def get_file_paths(self) -> list[Path]:
        file_paths = []
        all_items = self.filelist_treeview.get_children()
        for item_id in all_items:
            fullpath, _ = self.filelist_treeview.item(item_id, 'values')
            file_paths.append(Path(fullpath))
        return file_paths
