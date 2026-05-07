"""Worker 基类

定义 Worker 的统一接口。
"""
from abc import ABC, abstractmethod
from collections.abc import Callable

from core.states import TaskState

# 回调函数类型定义
ProgressCallback = Callable[[float, int], None]  # (value, total)
StatusCallback = Callable[[TaskState, str], None]  # (state, message)


class BaseWorker(ABC):
    """Worker 抽象基类

    所有具体的 Worker 都应该继承此类并实现 execute 方法。
    """

    @abstractmethod
    def execute(
        self,
        params: dict,
        progress_callback: ProgressCallback,
        status_callback: StatusCallback,
        cancel_event
    ) -> None:
        """执行处理任务

        Args:
            params: 任务参数，包含 inputs, output, options 等
            progress_callback: 进度回调函数，签名 (value: float, total: int = 0)
                              - value: 当前进度值（绝对值，如已处理的文件数）
                              - total: 进度最大值（仅在 PROCESS 阶段首次发送时有效）
            status_callback: 状态回调函数，签名 (state: TaskState, message: str)
            cancel_event: 取消事件，通过 cancel_event.is_set() 检查是否被取消

        Raises:
            TaskCancelledError: 当用户取消任务时抛出
            Exception: 其他异常会传递给 TaskManager
        """
        pass
