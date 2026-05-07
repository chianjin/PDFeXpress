"""合并 PDF Worker

实现 PDF 合并功能的后台处理逻辑。
"""
import pymupdf

from core.states import TaskCancelledError, TaskState
from core.workers.base_worker import BaseWorker


class MergePdfWorker(BaseWorker):
    """合并 PDF Worker"""

    def execute(self, params, progress_callback, status_callback, cancel_event):
        """执行 PDF 合并任务

        Args:
            params: 包含 inputs（输入文件列表）、output（输出文件路径）和 options（选项）
            progress_callback: 进度回调
            status_callback: 状态回调
            cancel_event: 取消事件
        """
        input_files = params['inputs']
        output_file = params['output']
        options = params.get('options', {})
        generate_bookmarks = options.get('generate_bookmarks', True)
        double_side_print = options.get('double_side_print', False)

        # 1. 初始化阶段
        total_files = len(input_files)
        status_callback(TaskState.INIT, f"准备处理 {total_files} 个文件...")

        if cancel_event.is_set():
            raise TaskCancelledError("任务已取消")

        # 2. 预处理完成，发送 PROCESS 状态和进度条最大值
        status_callback(TaskState.PROCESS, "正在处理...")
        progress_callback(0, total_files)  # 首次发送：value=0, total=总数

        # 3. 合并所有 PDF 文件
        toc_items = []  # 收集书签
        with pymupdf.open() as output_doc:
            for index, input_path in enumerate(input_files, 1):
                if cancel_event.is_set():
                    raise TaskCancelledError("任务已取消")

                status_callback(
                    TaskState.PROCESS,
                    f"正在处理第 {index}/{total_files} 个文件: {input_path.name}"
                )
                progress_callback(index)  # 后续发送：只传 value

                with pymupdf.open(input_path) as input_doc:
                    # 记录当前页码（用于书签）
                    start_page = len(output_doc)

                    # 合并 PDF
                    output_doc.insert_pdf(input_doc)

                    # 如果启用了生成书签，添加书签（PyMuPDF 页码从 1 开始）
                    if generate_bookmarks:
                        bookmark_title = input_path.stem
                        toc_items.append([1, bookmark_title, start_page + 1])

                    # 如果启用了双面打印且页数为奇数，插入空白页
                    if double_side_print and len(input_doc) % 2 == 1:
                        output_doc.new_page()

            # 设置所有书签
            if toc_items:
                output_doc.set_toc(toc_items)

            # 4. 保存阶段
            status_callback(TaskState.SAVE, "正在保存...")

            if cancel_event.is_set():
                raise TaskCancelledError("任务已取消")

            output_doc.save(output_file, garbage=4, deflate=True)

        # 5. 完成
        status_callback(TaskState.SUCCESS, "合并完成")
