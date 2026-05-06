from pathlib import Path
import tkinter as tk
from tkinter import ttk

from config import ICONS_PATH, PAGE_NUMBER_SYNTAX
from ui.components.path_picker import PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class ValueSpinbox(ttk.Frame):
    def __init__(self, master, label, unit, **kwargs):
        super().__init__(master)

        # 提取textvariable参数
        self._value = kwargs.pop('textvariable', None)

        ttk.Label(self, text=label).pack(side=tk.LEFT)
        spinbox = ttk.Spinbox(self, **kwargs)
        if self._value:
            spinbox.configure(textvariable=self._value)
        spinbox.pack(side=tk.LEFT)
        ttk.Label(self, text=unit).pack(side=tk.LEFT)

    def set_value(self, value):
        self._value.set(value)

    def get_value(self):
        return self._value.get()


class AddPageNumbersFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='add_page_numbers', output_mode='save')

    def _set_input_frame(self):
        self.input_path_picker = PathPicker(self.input_frame, mode='open')
        self.input_path_picker.pack(side=tk.TOP, fill=tk.X)

    def _get_auto_output_strategy(self):
        from utils.auto_output_helpers import setup_auto_output_single_to_single

        return lambda frame: setup_auto_output_single_to_single(
            frame.input_path_picker,
            frame.output_path_picker,
            path_generator=lambda input_path: input_path.parent / f'{input_path.stem}_页码.pdf',
        )

    def _set_options_frame(self):
        self._page_rule = tk.StringVar(value='')
        self._font_family = tk.StringVar(value='Times')
        self._font_style = tk.StringVar(value='常规')
        self._font_size = tk.IntVar(value=10)
        self._position_v = tk.StringVar(value='footer')
        self._position_h = tk.StringVar(value='center')
        self._margin_top = tk.DoubleVar(value=1.0)
        self._margin_bottom = tk.DoubleVar(value=1.0)
        self._margin_left = tk.DoubleVar(value=1.0)
        self._margin_right = tk.DoubleVar(value=1.0)
        self._margin_side = tk.DoubleVar(value=0.5)

        self._position_v.trace_add('write', self._update_margin_v_widgets)
        self._position_h.trace_add('write', self._update_margin_h_widgets)

        # 第一行：页码规则 + 帮助按钮
        rule_frame = ttk.Frame(self.options_frame)
        rule_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(rule_frame, text='页码规则：').pack(side=tk.LEFT)
        ttk.Entry(
            rule_frame,
            textvariable=self._page_rule,
            width=20,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(rule_frame, text='提示：从 1 开始连续数字编号。点击').pack(side=tk.LEFT)
        self._help_icon = tk.PhotoImage(file=ICONS_PATH / 'help.png')
        ttk.Button(
            rule_frame,
            image=self._help_icon,
            command=self._show_help,
            style='Toolbutton',
            padding=0,
        ).pack(side=tk.LEFT)
        ttk.Label(rule_frame, text='查看详细说明。').pack(side=tk.LEFT)

        # 第二行：字体、字形、字号
        font_frame = ttk.Frame(self.options_frame)
        font_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        ttk.Label(font_frame, text='字体：').pack(side=tk.LEFT)
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
        position_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        ttk.Label(position_frame, text='位置：').pack(side=tk.LEFT)
        ttk.Radiobutton(
            position_frame,
            text='页眉',
            value='header',
            variable=self._position_v,
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            position_frame,
            text='页脚',
            value='footer',
            variable=self._position_v,
        ).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Separator(position_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=20)

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
        ).pack(side=tk.LEFT)

        # 第四行：边距
        margin_frame = ttk.Frame(self.options_frame)
        margin_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self.margin_v_frame = ttk.Frame(margin_frame)
        self.margin_v_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.margin_h_frame = ttk.Frame(margin_frame)
        self.margin_h_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self._margin_widgets = {
            'margin_top': ValueSpinbox(
                self.margin_v_frame,
                '上边距：',
                '厘米',
                width=10,
                from_=0,
                to=10,
                increment=0.1,
                textvariable=self._margin_top,
            ),
            'margin_bottom': ValueSpinbox(
                self.margin_v_frame,
                '下边距：',
                '厘米',
                width=10,
                from_=0,
                to=10,
                increment=0.1,
                textvariable=self._margin_bottom,
            ),
            'margin_left': ValueSpinbox(
                self.margin_h_frame,
                '左边距：',
                '厘米',
                width=10,
                from_=0,
                to=10,
                increment=0.1,
                textvariable=self._margin_left,
            ),
            'margin_right': ValueSpinbox(
                self.margin_h_frame,
                '右边距：',
                '厘米',
                width=10,
                from_=0,
                to=10,
                increment=0.1,
                textvariable=self._margin_right,
            ),
            'margin_side': ValueSpinbox(
                self.margin_h_frame,
                '侧边距：',
                '厘米',
                width=10,
                from_=0,
                to=10,
                increment=0.1,
                textvariable=self._margin_side,
            ),
        }

        # Pack所有边距控件（初始只显示需要的）
        for widget in self._margin_widgets.values():
            widget.pack(side=tk.LEFT, padx=(0, 5))

        # 初始化当前显示的控件（根据默认值）
        # 默认：页脚(footer) + 居中(center)
        self._current_margin_v_widget = self._margin_widgets['margin_bottom']
        self._current_margin_h_widget = None  # 居中时不显示水平边距

        # 隐藏不需要的控件
        self._margin_widgets['margin_top'].pack_forget()
        self._margin_widgets['margin_left'].pack_forget()
        self._margin_widgets['margin_right'].pack_forget()
        self._margin_widgets['margin_side'].pack_forget()

    def _update_margin_v_widgets(self, *_args):
        """根据垂直位置（页眉/页脚）更新显示的边距控件"""
        # 隐藏当前控件
        self._current_margin_v_widget.pack_forget()

        # 选择新控件
        if self._position_v.get() == 'header':
            self._current_margin_v_widget = self._margin_widgets['margin_top']
        else:  # footer
            self._current_margin_v_widget = self._margin_widgets['margin_bottom']

        # 显示新控件（在margin_v_frame中pack即可）
        self._current_margin_v_widget.pack(side=tk.LEFT, padx=(0, 5))

    def _update_margin_h_widgets(self, *_args):
        """根据水平位置（左/中/右/外/内）更新显示的边距控件"""
        # 隐藏当前控件（如果存在）
        if self._current_margin_h_widget:
            self._current_margin_h_widget.pack_forget()

        # 选择新控件
        position = self._position_h.get()
        if position in ('left', 'right'):
            # 左侧或右侧：显示对应的边距
            self._current_margin_h_widget = self._margin_widgets[f'margin_{position}']
        elif position == 'center':
            # 居中：不显示水平边距
            self._current_margin_h_widget = None
        else:  # outer or inner
            # 外侧或内侧：显示侧边距
            self._current_margin_h_widget = self._margin_widgets['margin_side']

        # 显示新控件
        if self._current_margin_h_widget:
            self._current_margin_h_widget.pack(side=tk.LEFT, padx=(0, 5))

    def _show_help(self):
        """显示页码规则帮助信息"""
        from ui.components.help_window import HelpWindow

        with PAGE_NUMBER_SYNTAX.open('r', encoding='utf-8') as f:
            help_title = f.readline().strip()
            f.seek(0)
            help_text = f.read()

        HelpWindow(self.master, title=help_title, content=help_text)

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
            'margin_side': self._margin_side.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    app = AddPageNumbersFrame(root)
    app.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    app.mainloop()
