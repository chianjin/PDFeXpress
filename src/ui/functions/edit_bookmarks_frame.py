from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.path_picker import PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class EditBookmarksFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='edit_bookmarks', output_mode='save')

    def _set_input_frame(self):
        self.input_path_picker = PathPicker(self.input_frame, mode='open')
        self.input_path_picker.pack(side=tk.TOP, fill=tk.X)

    def _get_auto_output_strategy(self):
        from utils.auto_output_helpers import setup_auto_output_single_to_single

        return lambda frame: setup_auto_output_single_to_single(
            frame.input_path_picker,
            frame.output_path_picker,
            path_generator=lambda input_path: input_path.parent / f'{input_path.stem}_书签.pdf',
        )

    def _set_options_frame(self):
        self._level = tk.StringVar()
        self._page = tk.StringVar()
        self._title = tk.StringVar()

        # 主容器
        main_frame = ttk.Frame(self.options_frame)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(main_frame, text='书签').pack(side=tk.TOP, anchor='w')

        # Treeview和右侧按钮区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))

        # 左侧：Treeview
        tree_frame = ttk.Frame(content_frame)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ('level', 'page', 'title')
        self._bookmark_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=15,
        )

        # 设置列标题
        self._bookmark_tree.heading('level', text='层级')
        self._bookmark_tree.heading('page', text='页码')
        self._bookmark_tree.heading('title', text='标题')

        # 设置列宽
        self._bookmark_tree.column('level', width=60, anchor='center')
        self._bookmark_tree.column('page', width=60, anchor='center')
        self._bookmark_tree.column('title', width=400, anchor='w')

        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self._bookmark_tree.yview
        )
        self._bookmark_tree.configure(yscrollcommand=tree_scrollbar.set)

        self._bookmark_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧：按钮列
        button_column = ttk.Frame(content_frame)
        button_column.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self._reload_button = ttk.Button(
            button_column, text='重新加载', width=12, command=self._reload_bookmarks
        )
        self._reload_button.pack(side=tk.TOP, pady=(0, 5))

        separator1 = ttk.Separator(button_column, orient=tk.HORIZONTAL)
        separator1.pack(side=tk.TOP, fill=tk.X, pady=5)

        self._import_button = ttk.Button(
            button_column, text='导入', width=12, command=self._import_bookmarks
        )
        self._import_button.pack(side=tk.TOP, pady=(0, 5))

        self._export_button = ttk.Button(
            button_column, text='导出', width=12, command=self._export_bookmarks
        )
        self._export_button.pack(side=tk.TOP, pady=(0, 5))

        separator2 = ttk.Separator(button_column, orient=tk.HORIZONTAL)
        separator2.pack(side=tk.TOP, fill=tk.X, pady=5)

        self._move_up_button = ttk.Button(
            button_column, text='上移', width=12, command=self._move_up
        )
        self._move_up_button.pack(side=tk.TOP, pady=(0, 5))

        self._move_down_button = ttk.Button(
            button_column, text='下移', width=12, command=self._move_down
        )
        self._move_down_button.pack(side=tk.TOP, pady=(0, 5))

        separator3 = ttk.Separator(button_column, orient=tk.HORIZONTAL)
        separator3.pack(side=tk.TOP, fill=tk.X, pady=5)

        self._delete_button = ttk.Button(
            button_column, text='删除', width=12, command=self._delete_bookmark
        )
        self._delete_button.pack(side=tk.TOP, pady=(0, 5))

        self._clear_button = ttk.Button(
            button_column, text='全部删除', width=12, command=self._clear_all
        )
        self._clear_button.pack(side=tk.TOP)

        # 底部：输入行
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        ttk.Label(input_frame, text='层级：').pack(side=tk.LEFT)
        ttk.Entry(
            input_frame,
            textvariable=self._level,
            width=8,
        ).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(input_frame, text='页码：').pack(side=tk.LEFT)
        ttk.Entry(
            input_frame,
            textvariable=self._page,
            width=8,
        ).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(input_frame, text='标题：').pack(side=tk.LEFT)
        ttk.Entry(
            input_frame,
            textvariable=self._title,
            width=40,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        self._edit_button = ttk.Button(
            input_frame,
            text='编辑',
            width=10,
            command=self._edit_bookmark,
        )
        self._edit_button.pack(side=tk.RIGHT, padx=(5, 0))

        self._add_button = ttk.Button(
            input_frame,
            text='添加',
            width=10,
            command=self._add_bookmark,
        )
        self._add_button.pack(side=tk.RIGHT)

        # 存储所有书签数据
        self._bookmarks = []

    def _add_bookmark(self):
        """添加书签到列表"""
        level = self._level.get().strip()
        page = self._page.get().strip()
        title = self._title.get().strip()

        if not level or not page or not title:
            return

        # 添加到树形视图
        self._bookmark_tree.insert('', tk.END, values=(level, page, title))
        self._bookmarks.append({'level': int(level), 'page': int(page), 'title': title})

        # 清空输入框
        self._level.set('')
        self._page.set('')
        self._title.set('')

    def _edit_bookmark(self):
        """编辑选中的书签"""
        selection = self._bookmark_tree.selection()
        if not selection:
            return

        # 获取选中的项
        item = selection[0]
        values = self._bookmark_tree.item(item, 'values')

        # 填充到输入框
        self._level.set(values[0])
        self._page.set(values[1])
        self._title.set(values[2])

        # 删除旧项
        self._bookmark_tree.delete(item)

    def _delete_bookmark(self):
        """删除选中的书签"""
        selection = self._bookmark_tree.selection()
        if not selection:
            return

        for item in selection:
            self._bookmark_tree.delete(item)

        # 重新构建书签列表
        self._bookmarks = []
        for item in self._bookmark_tree.get_children():
            values = self._bookmark_tree.item(item, 'values')
            self._bookmarks.append({'level': int(values[0]), 'page': int(values[1]), 'title': values[2]})

    def _clear_all(self):
        """清空所有书签"""
        self._bookmark_tree.delete(*self._bookmark_tree.get_children())
        self._bookmarks = []

    def _reload_bookmarks(self):
        """重新加载书签"""
        # TODO: 从PDF重新加载书签
        pass

    def _import_bookmarks(self):
        """导入书签"""
        # TODO: 从文件导入书签
        pass

    def _export_bookmarks(self):
        """导出书签"""
        # TODO: 导出书签到文件
        pass

    def _move_up(self):
        """上移选中项"""
        selection = self._bookmark_tree.selection()
        if not selection:
            return

        item = selection[0]
        prev_item = self._bookmark_tree.prev(item)
        if prev_item:
            # 交换位置
            self._bookmark_tree.move(item, '', self._bookmark_tree.index(prev_item))
            self._update_bookmarks_list()

    def _move_down(self):
        """下移选中项"""
        selection = self._bookmark_tree.selection()
        if not selection:
            return

        item = selection[0]
        next_item = self._bookmark_tree.next(item)
        if next_item:
            # 交换位置
            self._bookmark_tree.move(next_item, '', self._bookmark_tree.index(item))
            self._update_bookmarks_list()

    def _update_bookmarks_list(self):
        """更新书签列表数据"""
        self._bookmarks = []
        for item in self._bookmark_tree.get_children():
            values = self._bookmark_tree.item(item, 'values')
            self._bookmarks.append({'level': int(values[0]), 'page': int(values[1]), 'title': values[2]})

    def get_input_files(self) -> list[Path]:
        input_path = self.input_path_picker.get()
        if input_path:
            return [Path(input_path)]
        return []

    def get_options(self) -> dict:
        return {
            'bookmarks': self._bookmarks,
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = EditBookmarksFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
