"""UI widget for file list with drag-and-drop support."""

from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Any

from tkinterdnd2 import DND_FILES

from toolkit.constant import FILE_TYPES_PDF
from toolkit.i18n import gettext_text as _
from toolkit.util.decorator import create_run_after_decorator
from toolkit.util.file_util import (
    get_files_with_extensions,
    get_folder_files_with_extensions,
)

check_file_list_change = create_run_after_decorator('_on_change_callback')


class FileListView(ttk.Labelframe):
    def __init__(
        self,
        parent: ttk.Frame,
        title: str = _('File List'),
        file_types: list = FILE_TYPES_PDF,
        sortable: bool = False,
        on_change_callback: Callable | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, text=title, **kwargs)

        self._file_types = file_types
        self._sortable = sortable
        self._on_change_callback = on_change_callback
        self._sort_ascending = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.treeview_frame = ttk.Frame(self)
        self.treeview_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.treeview_frame.rowconfigure(0, weight=1)
        self.treeview_frame.columnconfigure(0, weight=1)

        self.filelist_treeview = ttk.Treeview(
            self.treeview_frame,
            columns=('filepath',),
            show='headings',
            selectmode='extended',
        )

        self.filelist_treeview.heading('filepath', text=_('File Path'), anchor='w')
        self.filelist_treeview.column('filepath', width=300)

        self.filelist_scrollbar = ttk.Scrollbar(
            self.treeview_frame, orient='vertical', command=self.filelist_treeview.yview
        )
        self.filelist_treeview.configure(yscrollcommand=self.filelist_scrollbar.set)

        self.filelist_treeview.grid(row=0, column=0, sticky='nsew', padx=0)
        self.filelist_scrollbar.grid(row=0, column=1, sticky='ns', padx=0)

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=0, column=1, sticky='n', padx=5, pady=5)
        self.button_frame.columnconfigure(0, weight=1)

        self.button_row_counter = 0

        self.add_files_button = ttk.Button(
            self.button_frame, text=_('Add Files'), command=self._add_files
        )
        self.add_files_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(0, 5)
        )
        self.button_row_counter += 1

        self.add_folder_button = ttk.Button(
            self.button_frame, text=_('Add Folder'), command=self._add_folder
        )
        self.add_folder_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(0, 5)
        )
        self.button_row_counter += 1

        self.remove_files_button = ttk.Button(
            self.button_frame, text=_('Remove Files'), command=self._remove_files
        )
        self.remove_files_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(0, 5)
        )
        self.button_row_counter += 1

        self.remove_all_button = ttk.Button(
            self.button_frame, text=_('Remove All'), command=self._remove_all
        )
        self.remove_all_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(0, 5)
        )
        self.button_row_counter += 1

        if self._sortable:
            self._make_sortable()

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)

    def _make_sortable(self) -> None:
        self._add_sorting_buttons()
        self.filelist_treeview.heading('filepath', command=self._sort_filepath)

    def _add_sorting_buttons(self) -> None:
        separator = ttk.Separator(self.button_frame, orient='horizontal')
        separator.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(5, 5)
        )
        self.button_row_counter += 1

        self.move_to_first_button = ttk.Button(
            self.button_frame, text=_('Move to First'), command=self._move_to_first
        )
        self.move_to_first_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(5, 0)
        )
        self.button_row_counter += 1

        self.move_up_button = ttk.Button(
            self.button_frame, text=_('Move Up'), command=self._move_up
        )
        self.move_up_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(5, 0)
        )
        self.button_row_counter += 1

        self.move_down_button = ttk.Button(
            self.button_frame, text=_('Move Down'), command=self._move_down
        )
        self.move_down_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(5, 0)
        )
        self.button_row_counter += 1

        self.move_to_last_button = ttk.Button(
            self.button_frame, text=_('Move to Last'), command=self._move_to_last
        )
        self.move_to_last_button.grid(
            row=self.button_row_counter, column=0, sticky='ew', padx=0, pady=(5, 0)
        )
        self.button_row_counter += 1

    def _sort_filepath(self) -> None:
        items = [
            (self.filelist_treeview.set(k, 'filepath'), k)
            for k in self.filelist_treeview.get_children('')
        ]
        if not self._sort_ascending:
            items.sort(key=lambda x: x[0].lower())
            self._sort_ascending = True
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=True)
            self._sort_ascending = False

        for index, (filepath, k) in enumerate(items):
            self.filelist_treeview.move(k, '', index)

    @check_file_list_change
    def _add_files(self) -> bool | None:
        file_paths = filedialog.askopenfilenames(
            title=_('Select input files.'), filetypes=self._file_types
        )
        if not file_paths:
            return None

        for file_path in file_paths:
            self.filelist_treeview.insert('', 'end', values=(str(Path(file_path)),))

        return None

    @check_file_list_change
    def _add_folder(self) -> bool | None:
        folder_path = filedialog.askdirectory(title=_('Select input folder.'))
        if not folder_path:
            return None

        file_paths = get_folder_files_with_extensions(folder_path, self._file_types)
        for file_path in file_paths:
            self.filelist_treeview.insert('', 'end', values=(str(Path(file_path)),))

        return None

    @check_file_list_change
    def _remove_files(self, event: Any | None = None) -> bool | None:
        selected_items = self.filelist_treeview.selection()
        if not selected_items:
            return None

        for item in selected_items:
            self.filelist_treeview.delete(item)

        return None

    @check_file_list_change
    def _remove_all(self) -> None:
        for item in self.filelist_treeview.get_children():
            self.filelist_treeview.delete(item)

    @check_file_list_change
    def _move_to_first(self) -> None:
        selected_items = self.filelist_treeview.selection()
        if 0 < len(selected_items) < 2:
            item = self.filelist_treeview.selection()[0]
            self.filelist_treeview.move(item, '', 0)

    @check_file_list_change
    def _move_up(self) -> None:
        selected_items = self.filelist_treeview.selection()
        if 0 < len(selected_items) < 2:
            item = self.filelist_treeview.selection()[0]
            prev_item = self.filelist_treeview.prev(item)
            self.filelist_treeview.move(
                item, '', self.filelist_treeview.index(prev_item)
            )

    @check_file_list_change
    def _move_down(self) -> None:
        selected_items = self.filelist_treeview.selection()
        if 0 < len(selected_items) < 2:
            item = self.filelist_treeview.selection()[0]
            next_item = self.filelist_treeview.next(item)
            self.filelist_treeview.move(
                item, '', self.filelist_treeview.index(next_item)
            )

    @check_file_list_change
    def _move_to_last(self) -> None:
        selected_items = self.filelist_treeview.selection()
        if 0 < len(selected_items) < 2:
            item = self.filelist_treeview.selection()[0]
            self.filelist_treeview.move(item, '', 'end')

    @check_file_list_change
    def _on_drop(self, event: Any) -> None:
        top_level = self.winfo_toplevel()
        file_paths = top_level.tk.splitlist(event.data)
        file_paths = get_files_with_extensions(file_paths, self._file_types)
        for file_path in file_paths:
            self.filelist_treeview.insert('', 'end', values=(str(Path(file_path)),))

    def get(self) -> list[Path]:
        return [
            Path(self.filelist_treeview.item(item)['values'][0])
            for item in self.filelist_treeview.get_children()
        ]

    @check_file_list_change
    def set(self, file_paths: list[str] | list[Path]) -> bool | None:
        if not file_paths:
            self.clear()
            return None

        self.clear()
        for file_path in file_paths:
            self.filelist_treeview.insert('', 'end', values=(str(file_path),))

        return None

    def clear(self) -> None:
        for item in self.filelist_treeview.get_children():
            self.filelist_treeview.delete(item)


if __name__ == '__main__':
    import tkinterdnd2

    root = tkinterdnd2.Tk()
    root.title('File List Test')
    root.geometry('800x500')

    file_list2 = FileListView(root, title='Test File List', sortable=True)
    file_list2.pack(fill='both', expand=True, padx=10, pady=10)

    root.mainloop()
