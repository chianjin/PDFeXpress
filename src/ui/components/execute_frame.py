import tkinter as tk
from tkinter import ttk


class ExecuteFrame(ttk.LabelFrame):
    def __init__(self, master, execute_text='执行', **kwargs):
        super().__init__(master, text='执行', padding=5, **kwargs)
        self.execute_text = execute_text

        self.progress = tk.IntVar(value=0)
        self.status = tk.StringVar(value='就绪')

        # 进度条
        self.progress_bar = ttk.Progressbar(self, variable=self.progress)
        self.progress_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # 状态栏与按钮
        execute_frame = ttk.Frame(self)
        execute_frame.pack(side=tk.TOP, fill=tk.X)
        execute_frame.columnconfigure(0, weight=1)

        # 状态栏
        self.state_label = ttk.Label(execute_frame, textvariable=self.status)
        self.state_label.grid(row=0, column=0, sticky=tk.EW)
        self.execute_button = ttk.Button(
            execute_frame, text=execute_text, command=self._on_execute
        )
        self.execute_button.grid(row=0, column=1, padx=(5, 0))
        self.cancel_button = ttk.Button(execute_frame, text='取消', command=self._on_cancel)
        self.cancel_button.grid(row=0, column=2, padx=(5, 0))
        self.close_button = ttk.Button(execute_frame, text='关闭', command=self._on_close)
        self.close_button.grid(row=0, column=3, padx=(5, 0))

        self.cancel_button.config(state=tk.DISABLED)

    def _on_execute(self):
        pass

    def _on_cancel(self):
        pass

    def _on_close(self):

        top_window = self.winfo_toplevel()
        top_window.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    frame = ExecuteFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    root.mainloop()
