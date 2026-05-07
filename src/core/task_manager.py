"""任务管理器

负责管理后台进程的生命周期，提供消息队列给 ExecuteFrame。
"""
from multiprocessing import Event, Process, Queue
import time

from core.messages import CompleteMessage
from core.states import TaskCancelledError


class TaskManager:
    """任务管理器

    职责：
    - 根据 function_id 启动对应的 Worker
    - 管理后台进程生命周期
    - 提供消息队列给 ExecuteFrame 直接读取
    - 只在异常时向 ExecuteFrame 反馈
    """

    def __init__(self):
        self._worker_process: Process | None = None
        self._message_queue: Queue | None = None
        self._cancel_event: Event | None = None
        self._is_running = False
        self._start_time: float = 0
        self._timeout: int = 300  # 默认超时时间 300 秒

    @property
    def message_queue(self) -> Queue | None:
        """获取消息队列（供 ExecuteFrame 读取）"""
        return self._message_queue

    @property
    def is_running(self) -> bool:
        """任务是否正在运行"""
        return self._is_running

    def start(self, function_id: str, params: dict):
        """启动任务

        Args:
            function_id: 功能 ID，用于映射到对应的 Worker 类
            params: 任务参数，包含 inputs, output, options 等
        """
        # 清理之前的任务
        if self._is_running:
            self.stop()

        # 创建新的队列和取消事件
        self._message_queue = Queue()
        self._cancel_event = Event()
        self._is_running = True
        self._start_time = time.time()

        # 获取超时设置
        self._timeout = params.get('options', {}).get('timeout', 300)

        # 根据 function_id 获取 Worker 类
        worker_class = self._get_worker_class(function_id)

        # 启动后台进程
        self._worker_process = Process(
            target=self._run_worker,
            args=(worker_class, params, self._message_queue, self._cancel_event),
            daemon=True
        )
        self._worker_process.start()

    def cancel(self):
        """取消任务"""
        if self._cancel_event:
            self._cancel_event.set()

    def stop(self):
        """停止任务（强制终止）"""
        if self._worker_process and self._worker_process.is_alive():
            self._worker_process.terminate()
            self._worker_process.join(timeout=5)

        self._is_running = False
        self._worker_process = None
        self._message_queue = None
        self._cancel_event = None

    def check_timeout(self) -> CompleteMessage | None:
        """检查是否超时

        Returns:
            如果超时返回 CompleteMessage，否则返回 None
        """
        if self._worker_process and self._worker_process.is_alive():
            if time.time() - self._start_time > self._timeout:
                self._worker_process.terminate()
                self._is_running = False
                return CompleteMessage(
                    success=False,
                    error=TimeoutError(f"任务超时（{self._timeout}秒）")
                )
        return None

    @staticmethod
    def _run_worker(worker_class, params: dict, queue: Queue, cancel_event: Event):
        """在后台进程中运行 Worker

        Args:
            worker_class: Worker 类
            params: 任务参数
            queue: 消息队列
            cancel_event: 取消事件
        """
        try:
            worker = worker_class()

            # 封装回调函数
            def progress_callback(value: float, total: int = 0):
                from core.messages import ProgressMessage
                queue.put(ProgressMessage(value=value, total=total))

            def status_callback(state, message: str):
                from core.messages import StatusMessage
                queue.put(StatusMessage(state=state, message=message))

            # 执行任务
            worker.execute(params, progress_callback, status_callback, cancel_event)

            # 任务成功完成
            queue.put(CompleteMessage(success=True))

        except TaskCancelledError:
            # 用户主动取消
            queue.put(CompleteMessage(success=False, cancelled=True))

        except Exception as e:
            # 其他异常 - 打印到控制台以便调试
            import traceback
            print(f"\n{'='*60}")
            print(f"Worker 执行异常: {type(e).__name__}: {e}")
            print(f"{'='*60}")
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # 同时放入消息队列通知 UI
            queue.put(CompleteMessage(success=False, error=e))

    @staticmethod
    def _get_worker_class(function_id: str):
        """根据 function_id 获取 Worker 类

        Args:
            function_id: 功能 ID

        Returns:
            Worker 类

        Raises:
            ValueError: 如果 function_id 未注册
        """
        # 功能 ID 到 Worker 类的映射
        worker_mapping = {
            'merge_pdf': 'core.workers.merge_pdf_worker.MergePdfWorker',
            # 添加更多映射...
        }

        if function_id not in worker_mapping:
            raise ValueError(f"未知的功能 ID: {function_id}")

        # 动态导入 Worker 类
        module_path, class_name = worker_mapping[function_id].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
