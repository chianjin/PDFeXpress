import tkinter as tk
from tkinter import ttk

from core.messages import CompleteMessage, ProgressMessage, StatusMessage
from core.states import STATE_MESSAGES, TaskState
from core.task_manager import TaskManager


class ExecuteFrame(ttk.LabelFrame):
    def __init__(self, master, execute_text='执行', **kwargs):
        super().__init__(master, text='执行', padding=5, **kwargs)
        self.execute_text = execute_text

        # UI 变量
        self.progress = tk.IntVar(value=0)
        self.status = tk.StringVar(value='就绪')

        # 任务管理器
        self.task_manager = TaskManager()
        
        # 跟踪当前状态，避免重复切换进度条模式
        self._current_state: TaskState | None = None

        self._setup_ui()

    def _setup_ui(self):
        """设置 UI 组件"""
        # 进度条
        self.progress_bar = ttk.Progressbar(self, variable=self.progress)
        self.progress_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # 按钮框架
        execute_frame = ttk.Frame(self)
        execute_frame.pack(side=tk.TOP, fill=tk.X)
        execute_frame.columnconfigure(0, weight=1)

        # 状态标签
        self.state_label = ttk.Label(execute_frame, textvariable=self.status)
        self.state_label.grid(row=0, column=0, sticky=tk.EW)

        # 执行按钮
        self.execute_button = ttk.Button(
            execute_frame, text=self.execute_text, command=self._on_execute
        )
        self.execute_button.grid(row=0, column=1, padx=(5, 0))

        # 取消按钮
        self.cancel_button = ttk.Button(execute_frame, text='取消', command=self._on_cancel)
        self.cancel_button.grid(row=0, column=2, padx=(5, 0))

        # 关闭按钮
        self.close_button = ttk.Button(execute_frame, text='关闭', command=self._on_close)
        self.close_button.grid(row=0, column=3, padx=(5, 0))

        # 初始状态：禁用取消按钮
        self.cancel_button.config(state=tk.DISABLED)

    def set_execute_handler(self, handler):
        """设置执行处理器

        Args:
            handler: 返回 (function_id, params) 的函数
        """
        self._execute_handler = handler

    def reset_to_ready(self):
        """重置到就绪状态（当输入输出改变时调用）"""
        # 只有在任务完成后才重置，避免中断正在运行的任务
        if self.task_manager.is_running:
            return
        
        # 重置状态栏和进度条
        self.status.set('就绪')
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate', maximum=100)
        self.progress.set(0)
        
        # 重置当前状态跟踪
        self._current_state = None

    def _on_execute(self):
        """执行按钮点击"""
        if not self._execute_handler:
            return

        try:
            # 1. 立即禁用按钮（防止重复点击）
            self.execute_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.NORMAL)
            self.status.set('初始化：正在启动任务...')

            # 2. 启动进度条跑马灯（视觉上表示任务已启动）
            self.progress_bar.stop()
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start(10)

            # 3. 收集参数
            function_id, params = self._execute_handler()

            # 4. 启动任务
            self.task_manager.start(function_id, params)

            # 5. 启动消息检查定时器
            self.after(50, self._check_queue)

        except Exception as e:
            self.status.set(f'错误：{e!s}')
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
            self.progress.set(0)
            self.execute_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)

    def _on_cancel(self):
        """取消按钮点击"""
        self.task_manager.cancel()

    def _on_close(self):
        """关闭按钮点击"""
        self.task_manager.stop()
        top_window = self.winfo_toplevel()
        top_window.destroy()

    def _check_queue(self):
        """定期检查消息队列（直接从 Queue 读取）"""
        queue = self.task_manager.message_queue
        if not queue:
            return

        # 检查超时
        timeout_msg = self.task_manager.check_timeout()
        if timeout_msg:
            self._handle_message(timeout_msg)
            return

        # 取出所有消息，分类处理
        last_progress = None
        other_messages = []
        has_complete_message = False

        while not queue.empty():
            try:
                msg = queue.get_nowait()
                if isinstance(msg, ProgressMessage):
                    last_progress = msg  # 只保留最新的进度消息
                else:
                    other_messages.append(msg)  # 其他消息全部保留
                    if isinstance(msg, CompleteMessage):
                        has_complete_message = True
            except Exception:
                break

        # 先处理非进度消息（状态、完成等关键消息）
        for msg in other_messages:
            self._handle_message(msg)

        # 最后处理最新的进度消息
        if last_progress:
            self._handle_message(last_progress)

        # 如果收到了完成消息，不再检查进程状态
        if has_complete_message:
            return

        # 检查进程是否存活（仅在未收到完成消息时）
        if (self.task_manager._worker_process and
            not self.task_manager._worker_process.is_alive()):
            if self.task_manager.is_running:
                self._handle_message(CompleteMessage(
                    success=False,
                    error=RuntimeError("进程意外终止")
                ))
            return

        # 继续检查
        if self.task_manager.is_running:
            self.after(50, self._check_queue)

    def _handle_message(self, msg):
        """处理单个消息"""
        if isinstance(msg, ProgressMessage):
            self._handle_progress(msg.value, msg.total)

        elif isinstance(msg, StatusMessage):
            self._handle_status(msg.state, msg.message)

        elif isinstance(msg, CompleteMessage):
            self._handle_complete(msg.success, msg.cancelled, msg.error)

    def _handle_progress(self, value: float, total: int = 0):
        """处理进度消息

        Args:
            value: 当前进度值
            total: 进度最大值（仅在 PROCESS 阶段首次发送时有效）
        """
        print(f"[DEBUG] Progress: value={value}, total={total}")
        if total > 0:
            # PROCESS 阶段首次收到消息：设置进度条最大值
            print(f"[DEBUG] Setting progress bar maximum to {total}")
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate', maximum=total)
            self.progress.set(int(value))
        else:
            # 后续进度更新：直接设置进度值
            self.progress.set(int(value))
        print(f"[DEBUG] Progress bar value set to {self.progress.get()}")

    def _handle_status(self, state: TaskState, message: str):
        """处理状态消息"""
        print(f"[DEBUG] Status received: state={state.value}, message={message}")
        # 根据状态码获取中文显示
        state_cn = STATE_MESSAGES.get(state.value, state.value)
        self.status.set(f'{state_cn}：{message}')
        print(f"[DEBUG] Status label set to: '{state_cn}：{message}'")

        # 只在状态改变时切换进度条模式
        if state != self._current_state:
            print(f"[DEBUG] State changed from {self._current_state.value if self._current_state else 'None'} to {state.value}")
            
            # 根据状态切换进度条模式
            if state in (TaskState.INIT, TaskState.SAVE):
                # 不定模式（跑马灯）- 初始化或保存阶段
                print(f"[DEBUG] Switching to indeterminate mode for {state.value}")
                self.progress_bar.stop()           # 1. 停止之前的动画
                self.progress.set(0)               # 2. 数值归零
                self.progress_bar.configure(mode='indeterminate', maximum=100)  # 3. 切换模式并重置最大值
                self.progress_bar.start(10)        # 4. 重新启动
            elif state == TaskState.PROCESS:
                # 确定模式（Worker 会在第一条进度消息中设置 maximum）
                print(f"[DEBUG] Switching to determinate mode for PROCESS")
                self.progress_bar.stop()
                self.progress_bar.configure(mode='determinate')
                # 注意：不在这里设置 maximum，等待 Worker 发送第一条进度消息时设置
            
            # 更新当前状态
            self._current_state = state

        self._update_buttons(state)

    def _handle_complete(self, success: bool, cancelled: bool = False, error: Exception | None = None):
        """处理完成消息"""
        self.progress_bar.stop()
    
        if success:
            # 成功：进度条显示满，与“成功”状态语义一致
            self.progress_bar.configure(mode='determinate')
            self.progress.set(100)
            self.status.set('成功：任务完成')
        elif cancelled:
            # 取消：进度归零
            self.progress_bar.configure(mode='determinate')
            self.progress.set(0)
            self.status.set('已取消：任务已取消')
        else:
            # 错误：进度归零
            self.progress_bar.configure(mode='determinate')
            self.progress.set(0)
            if error:
                self.status.set(f'错误：{error!s}')
                import traceback
                traceback.print_exception(type(error), error, error.__traceback__)
    
        # 重置当前状态，为下次任务做准备
        self._current_state = None
            
        self._update_buttons(TaskState.SUCCESS)

    def _update_buttons(self, state: TaskState):
        """根据状态更新按钮"""
        if state in (TaskState.SUCCESS, TaskState.CANCEL, TaskState.ERROR):
            # 任务结束：启用执行，禁用取消
            self.execute_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)


if __name__ == '__main__':
    root = tk.Tk()
    frame = ExecuteFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    root.mainloop()
