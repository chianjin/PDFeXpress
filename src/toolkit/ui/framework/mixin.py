# src/toolkit/ui/framework/mixin.py
from tkinter import messagebox
import multiprocessing
import queue 

from toolkit.ui.framework.progress_dialog import ProgressDialog # 相对导入
from toolkit.i18n import gettext_text as _ # 相对导入

class TaskRunnerMixin:
    """    核心框架 Mixin。
    提供运行后台进程、轮询队列和显示进度的全套功能。
    """
    def __init__(self, status_callback=None, *args, **kwargs):
        self.progress_dialog = None
        self.worker_process = None
        self.cancel_event = None
        self.progress_queue = None
        self.result_queue = None
        self.status_callback = status_callback
        self.saving_ack_event = None # 用于同步保存操作

    # --- 1. "契约" (Abstract Methods) ---
    def _get_root_window(self):
        """[契约] 子类必须实现：返回顶层 tk.Tk() 窗口"""
        raise NotImplementedError



    def _prepare_task(self):
        """
        [契约] 子类必须实现：校验输入。
        成功: 返回 (target_function, args_tuple, initial_label)
        失败: 返回 None (并自己弹出错误框)
        """
        raise NotImplementedError

    # --- 2. "模板方法" (Template Method) ---
    def run_task_from_ui(self):
        """
        这是所有"开始"按钮的 command。
        它定义了 "准备 -> 执行" 的模板流程。
        """
        print(f"[{self.__class__.__name__}]: 任务运行被请求...")

        try:
            task_data = self._prepare_task()
        except Exception as e:
            print(f"在 _prepare_task 期间发生错误: {e}")
            messagebox.showerror(_("Internal Error"), _("Error preparing task:\n{}").format(e))
            return

        if task_data is None:
            print(f"[{self.__class__.__name__}]: 任务准备失败 (校验未通过)。")
            return

        try:
            target_function, args_tuple, initial_label = task_data
        except (ValueError, TypeError):
            messagebox.showerror(_("Internal Error"), _("Task prepared invalid data."))
            return

        self._execute_task(target_function, args_tuple, initial_label)

    # --- 3. 内部执行逻辑 (Private Implementation) ---
    def _execute_task(self, target_function, args_tuple, initial_label):
        print(f"[{self.__class__.__name__}]: 任务执行开始...")



        self.cancel_event = multiprocessing.Event()
        self.progress_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.saving_ack_event = multiprocessing.Event() # 创建用于同步保存操作的事件

        self.progress_dialog = ProgressDialog(
            self._get_root_window(), 
            _("Processing..."), # 进度框标题
            initial_label, # 进度框初始文本
            self.request_cancel
        )

        final_args = args_tuple + (self.cancel_event, self.progress_queue, self.result_queue, self.saving_ack_event)

        self.worker_process = multiprocessing.Process(target=target_function, args=final_args)
        self.worker_process.start()

        self._get_root_window().after(100, self.poll_queues)

    def poll_queues(self):
        """GUI 轮询器 (心跳)"""
        # 1. 优先检查结果队列
        try:
            result = self.result_queue.get_nowait()
            result_type, message = result

            # 任务结束
            if self.progress_dialog:
                self.progress_dialog.progressbar.stop() 
                if result_type == "SUCCESS":
                    self.progress_dialog.progressbar.config(mode='determinate', maximum=self.progress_dialog.progressbar['maximum'], value=self.progress_dialog.progressbar['maximum'])

            if result_type == "SUCCESS":
                messagebox.showinfo(_("Task Complete"), message)
                if self.status_callback:
                    self.status_callback(_("Task Complete: ") + message)
            elif result_type == "CANCEL":
                messagebox.showwarning(_("Task Cancelled"), message) 
                if self.status_callback:
                    self.status_callback(_("Task Cancelled: ") + message)
            elif result_type == "ERROR":
                messagebox.showerror(_("Error"), message)
                if self.status_callback:
                    self.status_callback(_("Error: ") + message)

            self.cleanup()
            return # 任务已结束，不再轮询

        except queue.Empty:
            pass # 结果队列为空，继续检查进度队列

        # 2. 检查进度队列
        try:
            msg = self.progress_queue.get_nowait()
            if not self.progress_dialog:
                pass # 或者处理一下，比如打印日志
            elif isinstance(msg, tuple):
                if msg[0] == "INIT":
                    # 切换到"确定"进度条
                    self.progress_dialog.label.config(text=_("Processing...")) 
                    self.progress_dialog.progressbar.stop() 
                    self.progress_dialog.progressbar.config(mode='determinate', maximum=msg[1], value=0)
                    if self.status_callback:
                        self.status_callback(_("Processing..."))
                elif msg[0] == "PROGRESS":
                    # 更新进度
                    self.progress_dialog.progressbar['value'] = msg[1]
                elif msg[0] == "SAVING":
                    # 切换到不定进度条并更新文本
                    self.progress_dialog.progressbar.stop()
                    self.progress_dialog.progressbar.config(mode='indeterminate')
                    self.progress_dialog.progressbar.start() # 启动不定模式动画，使用默认速度
                    self.progress_dialog.label.config(text=msg[1])
                    if self.status_callback:
                        self.status_callback(msg[1])
                    # 强制 UI 更新
                    self._get_root_window().update_idletasks() 
                    self.saving_ack_event.set() # 通知工作进程 UI 已处理 SAVING 消息
        except queue.Empty:
            pass # 没有进度消息

        # 安排下一次轮询
        self._get_root_window().after(100, self.poll_queues)

    def request_cancel(self):
        """取消请求"""
        print(f"[{self.__class__.__name__}]: 用户请求取消...")
        if self.cancel_event:
            self.cancel_event.set()

    def cleanup(self):
        """GUI 清理"""
        print(f"[{self.__class__.__name__}]: 执行清理...")

        if self.worker_process and self.worker_process.is_alive():
            self.worker_process.join(timeout=0.5) 

        if self.progress_dialog:
            self.progress_dialog.destroy()
            self.progress_dialog = None



        self.worker_process = None
        self.cancel_event = None
