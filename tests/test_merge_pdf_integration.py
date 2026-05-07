"""测试 MergePdfFrame 与新框架的集成"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import tkinter as tk
from ui.functions.merge_pdf_frame import MergePdfFrame
from core.task_manager import TaskManager


@pytest.fixture
def root():
    """创建 Tkinter root 窗口"""
    try:
        from tkinterdnd2 import Tk
        root = Tk()
        root.title("MergePdfFrame 集成测试")
        yield root
        root.destroy()
    except Exception:
        pytest.skip("TkinterDnD 环境不可用")


@pytest.fixture
def merge_pdf_frame(root):
    """创建 MergePdfFrame 实例"""
    frame = MergePdfFrame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    return frame


class TestMergePdfFrameIntegration:
    """测试 MergePdfFrame 集成"""

    def test_execute_handler_set(self, merge_pdf_frame):
        """测试执行处理器已设置"""
        assert merge_pdf_frame.execute_frame._execute_handler is not None

    def test_execute_handler_returns_correct_data(self, merge_pdf_frame):
        """测试执行处理器返回正确的数据"""
        function_id, params = merge_pdf_frame._execute_handler()
        
        assert function_id == 'merge_pdf'
        assert 'inputs' in params
        assert 'output' in params
        assert 'options' in params
        
        # 检查选项
        options = params['options']
        assert 'generate_bookmarks' in options
        assert 'double_side_print' in options

    def test_task_manager_integration(self, merge_pdf_frame):
        """测试 TaskManager 集成"""
        assert hasattr(merge_pdf_frame.execute_frame, 'task_manager')
        assert isinstance(merge_pdf_frame.execute_frame.task_manager, TaskManager)

    def test_worker_mapping(self):
        """测试 Worker 映射"""
        tm = TaskManager()
        worker_class = tm._get_worker_class('merge_pdf')
        
        from core.workers.merge_pdf_worker import MergePdfWorker
        assert worker_class == MergePdfWorker

    def test_options_passed_to_worker(self, merge_pdf_frame):
        """测试选项正确传递给 Worker"""
        # 修改选项
        merge_pdf_frame._generate_bookmarks.set(False)
        merge_pdf_frame._double_side_print.set(True)
        
        function_id, params = merge_pdf_frame._execute_handler()
        
        assert params['options']['generate_bookmarks'] is False
        assert params['options']['double_side_print'] is True
