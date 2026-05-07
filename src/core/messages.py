"""消息类型定义

用于后台进程和 UI 进程之间的通信。
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from core.states import TaskState


@dataclass
class ProgressMessage:
    """进度消息"""
    value: float  # 已处理的文件数或进度值
    total: int = 0  # 总数（仅在 INIT 阶段设置）


@dataclass
class StatusMessage:
    """状态消息"""
    state: TaskState
    message: str


@dataclass
class CompleteMessage:
    """完成消息"""
    success: bool
    cancelled: bool = False  # 是否为用户主动取消
    error: Exception | None = None


Message = Union[ProgressMessage, StatusMessage, CompleteMessage]
