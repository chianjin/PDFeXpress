from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilenames

from tkinterdnd2 import DND_FILES, Tk

from utils.file_types import FILE_TYPES
from utils.helpers import filter_dropped_files, filter_files


class FileListView(tk.Frame):
    def __init__(
        self,
        master,
        file_types=FILE_TYPES['PDF'],
        sortable: bool = True,
        allow_duplicates: bool = True,
    ):
        super().__init__(master)

        self._file_types = file_types
        self._sortable = sortable
        self._allow_duplicates = allow_duplicates
        self._sort_state = 'unknown'  # 'unknown', 'ascending', 'descending'
        self._first_file_var = tk.StringVar()  # 第一个文件路径（用于 trace 联动）

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
            self, columns=('fullpath', 'filename'), show='headings', selectmode='extended'
        )
        header_text = '文件名' if not self._sortable else '文件名 ❓'
        if self._sortable:
            self.filelist_treeview.heading(
                'filename', text=header_text, command=self._sort_filelist, anchor='w'
            )
        else:
            self.filelist_treeview.heading('filename', text=header_text, anchor='w')

        self.filelist_treeview.column('filename', anchor='w')
        self.filelist_treeview.column('fullpath', width=0, stretch=False, minwidth=0)

        self.filelist_treeview.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.filelist_treeview.yview)
        self.filelist_treeview.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

    def _create_buttons(self):

        buttons = [
            ('添加文件', self._add_files),
            ('添加文件夹', self._add_folder),
            ('移除选定', self._remove_selected),
            ('清空列表', self._clear_list),
        ]

        # 可排序模式添加额外按钮
        if self._sortable:
            buttons.append(('separator', None))
            buttons.extend(
                [
                    ('移至首位', self._move_to_top),
                    ('上移一位', self._move_up),
                    ('下移一位', self._move_down),
                    ('移至末尾', self._move_to_bottom),
                ]
            )

        botton_frame = tk.Frame(self)
        for text, command in buttons:
            if text == 'separator':
                ttk.Separator(botton_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(2, 7))
            else:
                ttk.Button(botton_frame, text=text, command=command).pack(fill=tk.X, pady=(0, 5))
        botton_frame.grid(row=0, column=2, sticky='nsew', padx=(5, 0))

    def _show_context_menu(self, event) -> None:
        self._context_menu.post(event.x_root, event.y_root)

    def _create_context_menu(self) -> None:
        """创建右键菜单"""
        self._context_menu = tk.Menu(self.filelist_treeview, tearoff=0)
        self._context_menu.add_command(label='全选', command=self._select_all)
        self._context_menu.add_command(label='反选', command=self._invert_selection)
        self._context_menu.add_command(label='清除选择', command=self._clear_selection)

        # 绑定右键事件
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
        """设置拖拽功能"""
        # 使用 tkinterdnd2 注册拖拽目标
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)

    def _on_drop(self, event):
        """处理拖拽释放事件"""
        paths = filter_dropped_files(event, self._file_types, include_folders=True)
        if not paths:
            return
        self._add_files_to_treeview(paths)

    def _update_header_text(self):
        """更新表头文本以反映当前排序状态"""
        if not self._sortable:
            return

        state_icons = {
            'unknown': '❓',
            'ascending': '⬆️',
            'descending': '⬇️',
        }
        icon = state_icons.get(self._sort_state, '❓')
        self.filelist_treeview.heading('filename', text=f'文件名 {icon}')

    def _sort_filelist(self):
        """根据当前排序状态对文件列表进行排序"""
        if not self._sortable:
            return

        # 获取所有项目数量，少于2个时不排序
        total_items = len(self.filelist_treeview.get_children())
        if total_items < 2:
            return

        # 确定新的排序状态：未知/降序 -> 升序，升序 -> 降序，降序 -> 升序
        if self._sort_state in ('unknown', 'descending'):
            new_state = 'ascending'
            reverse = False
        else:  # ascending
            new_state = 'descending'
            reverse = True

        # 获取所有项目及其文件名
        items = []
        for item_id in self.filelist_treeview.get_children():
            values = self.filelist_treeview.item(item_id, 'values')
            filename = values[1] if len(values) > 1 else values[0]
            items.append((item_id, filename))

        # 按文件名排序
        items.sort(key=lambda x: x[1].lower(), reverse=reverse)

        # 重新排列项目（移动到末尾会自动调整顺序）
        for item_id, _ in items:
            self.filelist_treeview.move(item_id, '', tk.END)

        # 更新排序状态和表头
        self._sort_state = new_state
        self._update_header_text()
        # 排序后第一个文件可能改变，更新第一个文件变量
        self._update_first_file_var()

    def _reset_sort_state(self):
        """重置排序状态为未知（在手动调整后调用）"""
        if self._sortable and self._sort_state != 'unknown':
            self._sort_state = 'unknown'
            self._update_header_text()

    def _get_existing_file_paths(self):
        """获取已添加的文件路径列表"""
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

            self.filelist_treeview.insert('', tk.END, values=(str(file_path), file_path.name))
            _changed = True

            if not self._allow_duplicates:
                existing_paths.add(str(file_path))

        if _changed:
            self._reset_sort_state()
            # 更新第一个文件变量（触发 auto_output 联动）
            self._update_first_file_var()

    def _update_first_file_var(self):
        """更新第一个文件路径变量"""
        files = self.get_file_paths()
        if files:
            self._first_file_var.set(str(files[0]))
        else:
            self._first_file_var.set('')

    def get_first_file_var(self):
        """获取第一个文件的 StringVar（供外部 trace 监听）"""
        return self._first_file_var

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
        # 更新第一个文件变量
        self._update_first_file_var()

    def _clear_list(self):
        all_items = self.filelist_treeview.get_children()
        for item in all_items[::-1]:
            self.filelist_treeview.delete(item)
        self._reset_sort_state()
        # 清空后更新第一个文件变量
        self._update_first_file_var()

    def _move_to_top(self):
        selected = self.filelist_treeview.selection()
        if not selected:
            return
        for item in selected[::-1]:
            index = self.filelist_treeview.index(item)
            if index == 0:
                continue
            self.filelist_treeview.move(item, '', 0)
        # 手动调整后重置排序状态
        self._reset_sort_state()
        # 更新第一个文件变量（可能改变了第一个文件）
        self._update_first_file_var()

    def _move_up(self):
        selected = self.filelist_treeview.selection()
        if not selected:
            return
        for item in selected:
            index = self.filelist_treeview.index(item)
            if index == 0:
                continue
            self.filelist_treeview.move(item, '', index - 1)
        # 手动调整后重置排序状态
        self._reset_sort_state()
        # 更新第一个文件变量（可能改变了第一个文件）
        self._update_first_file_var()

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
        # 手动调整后重置排序状态
        self._reset_sort_state()
        # 更新第一个文件变量（可能改变了第一个文件）
        self._update_first_file_var()

    def _move_to_bottom(self):
        selected = self.filelist_treeview.selection()
        if not selected:
            return
        total_items = len(self.filelist_treeview.get_children())
        for item in selected:
            self.filelist_treeview.move(item, '', total_items - 1)
        # 手动调整后重置排序状态
        self._reset_sort_state()
        # 更新第一个文件变量（可能改变了第一个文件）
        self._update_first_file_var()

    def get_file_paths(self) -> list[Path]:
        """获取文件列表"""
        file_paths = []
        all_items = self.filelist_treeview.get_children()
        for item_id in all_items:
            fullpath, _ = self.filelist_treeview.item(item_id, 'values')
            file_paths.append(Path(fullpath))
        return file_paths


if __name__ == '__main__':
    root = Tk()
    FileListView(root).pack(fill='both', expand=True, padx=10, pady=10)
    FileListView(root, allow_duplicates=False).pack(fill='both', expand=True, padx=10, pady=10)
    root.mainloop()
