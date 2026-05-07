"""测试任务执行框架的基本功能"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
from core.states import TaskState, TaskCancelledError, STATE_MESSAGES
from core.messages import ProgressMessage, StatusMessage, CompleteMessage
from core.workers.base_worker import BaseWorker, ProgressCallback, StatusCallback
from core.workers.merge_pdf_worker import MergePdfWorker
from core.task_manager import TaskManager


class TestStates:
    """测试状态枚举和异常"""

    def test_task_state_enum(self):
        """测试 TaskState 枚举"""
        assert hasattr(TaskState, 'READY')
        assert hasattr(TaskState, 'INIT')
        assert hasattr(TaskState, 'PROCESS')
        assert hasattr(TaskState, 'SAVE')
        assert hasattr(TaskState, 'SUCCESS')
        assert hasattr(TaskState, 'CANCEL')
        assert hasattr(TaskState, 'ERROR')

    def test_state_messages(self):
        """测试状态消息映射"""
        assert isinstance(STATE_MESSAGES, dict)
        # STATE_MESSAGES 的键是字符串，不是枚举
        assert 'READY' in STATE_MESSAGES
        assert 'SUCCESS' in STATE_MESSAGES

    def test_task_cancelled_error(self):
        """测试 TaskCancelledError 异常"""
        with pytest.raises(TaskCancelledError) as exc_info:
            raise TaskCancelledError("测试取消")
        
        assert "测试取消" in str(exc_info.value)


class TestMessages:
    """测试消息类"""

    def test_progress_message(self):
        """测试进度消息"""
        msg = ProgressMessage(value=5, total=10)
        assert msg.value == 5
        assert msg.total == 10

    def test_status_message(self):
        """测试状态消息"""
        msg = StatusMessage(state=TaskState.PROCESS, message="测试")
        assert msg.state == TaskState.PROCESS
        assert msg.message == "测试"

    def test_complete_message_success(self):
        """测试成功完成消息"""
        msg = CompleteMessage(success=True)
        assert msg.success is True
        assert msg.cancelled is False
        assert msg.error is None

    def test_complete_message_cancelled(self):
        """测试取消完成消息"""
        msg = CompleteMessage(success=False, cancelled=True)
        assert msg.success is False
        assert msg.cancelled is True
        assert msg.error is None

    def test_complete_message_error(self):
        """测试错误完成消息"""
        error = ValueError("测试错误")
        msg = CompleteMessage(success=False, error=error)
        assert msg.success is False
        assert msg.cancelled is False
        assert msg.error == error


class TestWorkers:
    """测试 Worker 类"""

    def test_base_worker_import(self):
        """测试 BaseWorker 导入"""
        assert BaseWorker is not None
        assert callable(ProgressCallback)
        assert callable(StatusCallback)

    def test_merge_pdf_worker_import(self):
        """测试 MergePdfWorker 导入"""
        assert MergePdfWorker is not None
        assert hasattr(MergePdfWorker, 'execute')


class TestTaskManager:
    """测试任务管理器"""

    def test_task_manager_creation(self):
        """测试 TaskManager 创建"""
        tm = TaskManager()
        assert tm.is_running is False
        assert tm.message_queue is None

    def test_task_manager_attributes(self):
        """测试 TaskManager 属性"""
        tm = TaskManager()
        assert hasattr(tm, 'start')
        assert hasattr(tm, 'stop')
        assert hasattr(tm, 'cancel')
        assert hasattr(tm, 'check_timeout')
        assert hasattr(tm, 'message_queue')
        assert hasattr(tm, 'is_running')
