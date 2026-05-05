from pathlib import Path
import tkinter as tk
from tkinter import ttk

from ui.components import PathPicker
from ui.functions.base_function_frame import BaseFunctionFrame


class InterleaveMergeFrame(BaseFunctionFrame):
    def __init__(self, master):
        super().__init__(master, function_id='interleave_merge')

    def _set_input_frame(self):
        """创建输入文件框架"""

        self.input_frame.columnconfigure(1, weight=1)

        ttk.Label(self.input_frame, text='PDF A').grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5)
        )
        self.input_patha_picker = PathPicker(self.input_frame, mode='open')
        self.input_patha_picker.grid(row=0, column=1, sticky=tk.EW, pady=(0, 5))
        self.input_patha_picker.set_trace('write', self._set_output_path)

        ttk.Label(self.input_frame, text='PDF B').grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.input_pathb_picker = PathPicker(self.input_frame, mode='open')
        self.input_pathb_picker.grid(row=1, column=1, sticky=tk.EW)

    def _set_options_frame(self):
        """创建选项框架"""
        self._revert_pdfb = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.options_frame,
            text='PDF B 逆序',
            variable=self._revert_pdfb,
            onvalue=True,
            offvalue=False,
        ).pack(anchor=tk.W)

    def _set_output_path(self, *_args):
        """设置输出路径（仅在 auto_output 启用时）"""
        if not self.output_path_picker.is_auto_output_enabled():
            return
            
        output_path = self.input_patha_picker.get_path().with_suffix('')
        output_path = f'{output_path}_交错合并.pdf'
        self.output_path_picker.set_path(output_path)

    def get_input_files(self) -> tuple[Path, ...]:
        """获取输入文件列表"""
        return self.input_patha_picker.get_path(), self.input_pathb_picker.get_path()

    def get_options(self) -> dict:
        """获取选项"""
        return {
            'revert_pdfb': self._revert_pdfb.get(),
        }


if __name__ == '__main__':
    from tkinterdnd2 import Tk

    root = Tk()
    frame = InterleaveMergeFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    root.update_idletasks()
    root.mainloop()
