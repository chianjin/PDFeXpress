from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components.path_picker import PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class AddPageNumbersFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='add_page_numbers', output_mode='save')

    def _set_input_frame(self):
        self.input_path_picker = PathPicker(self.input_frame, mode='open')
        self.input_path_picker.pack(side=tk.TOP, fill=tk.X)

    def _generate_output_filename(self, first_file: Path) -> str:
        return f"{first_file.stem}_页码.pdf"

    def _set_options_frame(self):
        self._page_rule = tk.StringVar(value='从1开始连续数字编号')
        self._font_family = tk.StringVar(value='Times')
        self._font_style = tk.StringVar(value='regular')
        self._font_size = tk.IntVar(value=10)
        self._position_v = tk.StringVar(value='footer')
        self._position_h = tk.StringVar(value='center')
        self._margin_top = tk.DoubleVar(value=1.0)
        self._margin_bottom = tk.DoubleVar(value=1.0)
        self._margin_left = tk.DoubleVar(value=1.0)
        self._margin_right = tk.DoubleVar(value=1.0)
        self._margin_gap = tk.DoubleVar(value=0.5)

        # 第一行：页码规则 + 帮助按钮
        rule_frame = ttk.Frame(self.options_frame)
        rule_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(rule_frame, text='页码规则:').pack(side=tk.LEFT)
        ttk.Entry(
            rule_frame,
            textvariable=self._page_rule,
            width=40,
        ).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(
            rule_frame,
            text='?',
            width=2,
            command=self._show_help,
        ).pack(side=tk.LEFT)

        # 第二行：字体、字形、字号
        font_frame = ttk.Frame(self.options_frame)
        font_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(font_frame, text='字体:').pack(side=tk.LEFT)
        ttk.Combobox(
            font_frame,
            textvariable=self._font_family,
            values=['Courier', 'Helvetica', 'Times'],
            state='readonly',
            width=10,
        ).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(font_frame, text='字形:').pack(side=tk.LEFT)
        ttk.Combobox(
            font_frame,
            textvariable=self._font_style,
            values=['常规', '斜体', '粗体', '粗斜体'],
            state='readonly',
            width=8,
        ).pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(font_frame, text='字号:').pack(side=tk.LEFT)
        ttk.Spinbox(
            font_frame,
            from_=6,
            to=20,
            textvariable=self._font_size,
            width=5,
        ).pack(side=tk.LEFT, padx=(5, 0))

        # 第三行：位置（垂直 + 水平）
        position_frame = ttk.Frame(self.options_frame)
        position_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(position_frame, text='位置:').pack(side=tk.LEFT)
        ttk.Radiobutton(
            position_frame,
            text='页眉',
            value='header',
            variable=self._position_v,
        ).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(
            position_frame,
            text='页脚',
            value='footer',
            variable=self._position_v,
        ).pack(side=tk.LEFT, padx=(5, 15))

        ttk.Separator(position_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Radiobutton(
            position_frame,
            text='左侧',
            value='left',
            variable=self._position_h,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(
            position_frame,
            text='居中',
            value='center',
            variable=self._position_h,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(
            position_frame,
            text='右侧',
            value='right',
            variable=self._position_h,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(
            position_frame,
            text='外侧',
            value='outer',
            variable=self._position_h,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(
            position_frame,
            text='内侧',
            value='inner',
            variable=self._position_h,
        ).pack(side=tk.LEFT, padx=(0, 0))

        # 第四行：边距
        margin_frame = ttk.Frame(self.options_frame)
        margin_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(margin_frame, text='上边距:').pack(side=tk.LEFT)
        ttk.Spinbox(
            margin_frame,
            from_=0,
            to=10,
            increment=0.1,
            textvariable=self._margin_top,
            width=6,
            format='%.1f',
        ).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(margin_frame, text='cm').pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(margin_frame, text='下边距:').pack(side=tk.LEFT)
        ttk.Spinbox(
            margin_frame,
            from_=0,
            to=10,
            increment=0.1,
            textvariable=self._margin_bottom,
            width=6,
            format='%.1f',
        ).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(margin_frame, text='cm').pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(margin_frame, text='左边距:').pack(side=tk.LEFT)
        ttk.Spinbox(
            margin_frame,
            from_=0,
            to=10,
            increment=0.1,
            textvariable=self._margin_left,
            width=6,
            format='%.1f',
        ).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(margin_frame, text='cm').pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(margin_frame, text='右边距:').pack(side=tk.LEFT)
        ttk.Spinbox(
            margin_frame,
            from_=0,
            to=10,
            increment=0.1,
            textvariable=self._margin_right,
            width=6,
            format='%.1f',
        ).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(margin_frame, text='cm').pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(margin_frame, text='边距:').pack(side=tk.LEFT)
        ttk.Spinbox(
            margin_frame,
            from_=0,
            to=10,
            increment=0.1,
            textvariable=self._margin_gap,
            width=6,
            format='%.1f',
        ).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(margin_frame, text='cm').pack(side=tk.LEFT)

    def _show_help(self):
        """显示页码规则帮助信息"""
        from ui.components.help_window import HelpWindow
        help_text = """页码规则说明：

基本语法：
- {n} - 当前页码
- {N} - 总页数
- {section} - 章节号

示例：
- "第{n}页" → 第1页, 第2页...
- "{n}/{N}" → 1/10, 2/10...
- "Section {section}-{n}" → Section 1-1, Section 1-2...

高级用法请参考完整文档。
"""
        HelpWindow(self.master, title='页码规则帮助', content=help_text)

    def get_input_files(self) -> list[Path]:
        input_path = self.input_path_picker.get()
        if input_path:
            return [Path(input_path)]
        return []

    def get_options(self) -> dict:
        return {
            'page_rule': self._page_rule.get(),
            'font_family': self._font_family.get(),
            'font_style': self._font_style.get(),
            'font_size': self._font_size.get(),
            'position_v': self._position_v.get(),
            'position_h': self._position_h.get(),
            'margin_top': self._margin_top.get(),
            'margin_bottom': self._margin_bottom.get(),
            'margin_left': self._margin_left.get(),
            'margin_right': self._margin_right.get(),
            'margin_gap': self._margin_gap.get(),
        }
