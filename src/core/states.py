"""任务状态枚举

定义任务执行过程中的各种状态。
"""
from enum import Enum

# 状态消息映射表（英文状态码 -> 中文显示）
STATE_MESSAGES = {
    'READY': '就绪',
    'INIT': '初始化',
    'PROCESS': '处理中',
    'SAVE': '保存中',
    'SUCCESS': '成功',
    'CANCEL': '已取消',
    'ERROR': '错误',
}


class TaskState(Enum):
    """任务状态枚举"""
    READY = 'READY'
    INIT = 'INIT'
    PROCESS = 'PROCESS'
    SAVE = 'SAVE'
    SUCCESS = 'SUCCESS'
    CANCEL = 'CANCEL'
    ERROR = 'ERROR'


class TaskCancelledError(Exception):
    """任务取消异常（用户主动取消）"""
    pass
