"""测试 ExecuteFrame UI 组件"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import tkinter as tk
from ui.components.execute_frame import ExecuteFrame
from core.task_manager import TaskManager
from core.messages import ProgressMessage, StatusMessage, CompleteMessage
from core.states import TaskState


@pytest.fixture
def root():
    """创建 Tkinter root 窗口"""
    try:
        root = tk.Tk()
        root.title("ExecuteFrame 测试")
        yield root
        root.destroy()
    except tk.TclError:
        pytest.skip("Tkinter 环境不可用")


@pytest.fixture
def execute_frame(root):
    """创建 ExecuteFrame 实例"""
    frame = ExecuteFrame(root, execute_text='测试执行')
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    return frame


class TestExecuteFrameCreation:
    """测试 ExecuteFrame 创建"""

    def test_frame_creation(self, execute_frame):
        """测试 ExecuteFrame 创建成功"""
        assert execute_frame is not None

    def test_execute_handler_setter(self, execute_frame):
        """测试设置执行处理器"""
        def test_handler():
            function_id = 'merge_pdf'
            params = {
                'inputs': [Path('test1.pdf'), Path('test2.pdf')],
                'output': Path('output.pdf'),
                'options': {}
            }
            return function_id, params

        execute_frame.set_execute_handler(test_handler)
        assert execute_frame._execute_handler == test_handler


class TestTaskManagerIntegration:
    """测试 TaskManager 集成"""

    def test_task_manager_attribute(self, execute_frame):
        """测试 task_manager 属性存在"""
        assert hasattr(execute_frame, 'task_manager')
        assert isinstance(execute_frame.task_manager, TaskManager)


class TestUIComponents:
    """测试 UI 组件"""

    def test_ui_components_exist(self, execute_frame):
        """测试所有 UI 组件存在"""
        assert hasattr(execute_frame, 'progress_bar')
        assert hasattr(execute_frame, 'execute_button')
        assert hasattr(execute_frame, 'cancel_button')
        assert hasattr(execute_frame, 'close_button')
        assert hasattr(execute_frame, 'state_label')


class TestInitialState:
    """测试初始状态"""

    def test_initial_button_states(self, execute_frame, root):
        """测试初始按钮状态"""
        root.update()  # 确保 UI 完全初始化
        execute_state = str(execute_frame.execute_button.cget('state'))
        cancel_state = str(execute_frame.cancel_button.cget('state'))
        
        assert execute_state == 'normal', f"执行按钮初始状态错误: {execute_state}"
        assert cancel_state == 'disabled', f"取消按钮初始状态错误: {cancel_state}"

    def test_initial_status_text(self, execute_frame, root):
        """测试初始状态文本"""
        root.update()
        assert execute_frame.status.get() == '就绪', f"初始状态文本错误: {execute_frame.status.get()}"

    def test_initial_progress_value(self, execute_frame, root):
        """测试初始进度值"""
        root.update()
        assert execute_frame.progress.get() == 0, f"初始进度值错误: {execute_frame.progress.get()}"


class TestMessageHandlers:
    """测试消息处理方法"""

    def test_message_handler_methods_exist(self, execute_frame):
        """测试所有消息处理方法存在"""
        assert hasattr(execute_frame, '_handle_message')
        assert hasattr(execute_frame, '_handle_progress')
        assert hasattr(execute_frame, '_handle_status')
        assert hasattr(execute_frame, '_handle_complete')


class TestProgressHandling:
    """测试进度处理"""

    def test_handle_progress_with_total(self, execute_frame):
        """测试带总数的进度消息处理"""
        execute_frame._handle_progress(5, 10)
        # 应该切换到 determinate 模式并设置最大值
        mode = str(execute_frame.progress_bar.cget('mode'))
        assert mode == 'determinate'
        assert execute_frame.progress_bar.cget('maximum') == 10

    def test_handle_progress_without_total(self, execute_frame):
        """测试不带总数的进度消息处理"""
        # 先设置一个初始状态
        execute_frame.progress_bar.configure(mode='determinate', maximum=10)
        execute_frame._handle_progress(7)
        # 应该只更新进度值
        assert execute_frame.progress.get() == 7


class TestStatusHandling:
    """测试状态处理"""

    def test_handle_status_message(self, execute_frame):
        """测试状态消息处理"""
        execute_frame._handle_status(TaskState.PROCESS, "测试中")
        assert "测试中" in execute_frame.status.get()


class TestCompleteHandling:
    """测试完成处理"""

    def test_handle_complete_success(self, execute_frame, root):
        """测试成功完成消息处理"""
        execute_frame._handle_complete(True, False, None)
        root.update()
        
        assert execute_frame.progress.get() == 100, "成功后进度应该为 100"
        assert "成功" in execute_frame.status.get()

    def test_handle_complete_cancelled(self, execute_frame, root):
        """测试取消完成消息处理"""
        execute_frame._handle_complete(False, True, None)
        root.update()
        
        assert execute_frame.progress.get() == 0, "取消后进度应该为 0"
        assert "取消" in execute_frame.status.get()

    def test_handle_complete_error(self, execute_frame, root):
        """测试错误完成消息处理"""
        execute_frame._handle_complete(False, False, ValueError("测试错误"))
        root.update()
        
        assert execute_frame.progress.get() == 0, "错误后进度应该为 0"
        assert "错误" in execute_frame.status.get()


class TestTaskManagerBasic:
    """测试 TaskManager 基本功能"""

    def test_task_manager_initial_state(self):
        """测试 TaskManager 初始状态"""
        tm = TaskManager()
        assert tm.is_running is False, "初始状态应该是未运行"
        assert tm.message_queue is None, "初始队列应该是 None"
