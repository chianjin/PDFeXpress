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

        # 书签输入区域
        input_frame = ttk.Frame(self.options_frame)
        input_frame.pack(side=tk.TOP, fill=tk.X)

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
            width=30,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        # 按钮区域
        button_frame = ttk.Frame(self.options_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self._add_button = ttk.Button(
            button_frame,
            text='添加',
            width=10,
            command=self._add_bookmark,
        )
        self._add_button.pack(side=tk.RIGHT, padx=(5, 0))

        self._edit_button = ttk.Button(
            button_frame,
            text='编辑',
            width=10,
            command=self._edit_bookmark,
        )
        self._edit_button.pack(side=tk.RIGHT, padx=(5, 0))

        self._delete_button = ttk.Button(
            button_frame,
            text='删除',
            width=10,
            command=self._delete_bookmark,
        )
        self._delete_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 书签列表区域
        list_frame = ttk.Frame(self.options_frame)
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10, 0))

        # 创建 Treeview
        columns = ('level', 'page', 'title')
        self._bookmark_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=10,
        )

        # 设置列标题
        self._bookmark_tree.heading('level', text='层级')
        self._bookmark_tree.heading('page', text='页码')
        self._bookmark_tree.heading('title', text='标题')

        # 设置列宽
        self._bookmark_tree.column('level', width=60, anchor='center')
        self._bookmark_tree.column('page', width=60, anchor='center')
        self._bookmark_tree.column('title', width=300, anchor='w')

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self._bookmark_tree.yview)
        self._bookmark_tree.configure(yscrollcommand=scrollbar.set)

        self._bookmark_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
        self._bookmarks.append({'level': level, 'page': page, 'title': title})

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
            self._bookmarks.append({'level': values[0], 'page': values[1], 'title': values[2]})

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
