"""合并 PDF Worker

实现 PDF 合并功能的后台处理逻辑。
"""
import time
import pymupdf

from core.states import TaskCancelledError, TaskState
from core.task_manager import WorkerBusinessError
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
        options = params['options']
        generate_bookmarks = options['generate_bookmarks']
        double_side_print = options['double_side_print']

        # 1. 初始化阶段
        print(f"[WORKER DEBUG] Step 1: INIT state")
        total_files = len(input_files)
        status_callback(TaskState.INIT, f"准备处理 {total_files} 个文件...")
        print(f"[WORKER DEBUG] Sent INIT status, sleeping 2s...")
        time.sleep(2)  # 模拟初始化耗时

        if cancel_event.is_set():
            raise TaskCancelledError("任务已取消")

        # 2. 预处理完成，发送 PROCESS 状态和进度条最大值
        print(f"[WORKER DEBUG] Step 2: Switching to PROCESS state")
        status_callback(TaskState.PROCESS, "正在处理...")
        print(f"[WORKER DEBUG] Sent PROCESS status, sending progress init (0, {total_files})")
        progress_callback(0, total_files)  # 首次发送：value=0, total=总数
        print(f"[WORKER DEBUG] Sleeping 1s before processing files...")
        time.sleep(1)

        # 3. 合并所有 PDF 文件
        print(f"[WORKER DEBUG] Step 3: Processing {total_files} files")
        toc_items = []  # 收集书签
        with pymupdf.open() as output_doc:
            for index, input_path in enumerate(input_files, 1):
                print(f"[WORKER DEBUG] --- Processing file {index}/{total_files}: {input_path.name}")
                
                if cancel_event.is_set():
                    raise TaskCancelledError("任务已取消")

                status_callback(
                    TaskState.PROCESS,
                    f"正在处理第 {index}/{total_files} 个文件: {input_path.name}"
                )
                print(f"[WORKER DEBUG] Sent PROCESS status for file {index}")
                progress_callback(index)  # 后续发送：只传 value
                print(f"[WORKER DEBUG] Sent progress {index}/{total_files}, sleeping 2s...")
                time.sleep(2)  # 模拟文件处理耗时

                try:
                    with pymupdf.open(input_path) as input_doc:
                        # 记录当前页码（用于书签）
                        current_total_page = len(output_doc)

                        # 合并 PDF
                        output_doc.insert_pdf(input_doc)

                        # 如果启用了生成书签，添加书签（PyMuPDF 页码从 1 开始）
                        if generate_bookmarks:
                            bookmark_title = input_path.stem
                            toc_items.append([1, bookmark_title, current_total_page + 1])

                        # 如果启用了双面打印且页数为奇数，插入空白页
                        if double_side_print and len(input_doc) % 2 == 1:
                            output_doc.new_page()
                except Exception as e:
                    raise WorkerBusinessError(f"无法打开文件: {input_path.name}\n{str(e)}")

            # 设置所有书签
            print(f"[WORKER DEBUG] Setting {len(toc_items)} bookmarks")
            if toc_items:
                output_doc.set_toc(toc_items)
                print(f"[WORKER DEBUG] Bookmarks set, sleeping 1s...")
                time.sleep(1)

            # 4. 保存阶段
            print(f"[WORKER DEBUG] Step 4: SAVE state")
            status_callback(TaskState.SAVE, "正在保存...")
            print(f"[WORKER DEBUG] Sent SAVE status, sleeping 3s to simulate save...")
            time.sleep(3)  # 模拟保存耗时

            if cancel_event.is_set():
                raise TaskCancelledError("任务已取消")

            try:
                print(f"[WORKER DEBUG] Saving to {output_file}")
                output_doc.save(output_file, garbage=4, deflate=True)
                print(f"[WORKER DEBUG] File saved successfully")
            except Exception as e:
                print(f"[WORKER DEBUG] Save failed: {e}")
                raise WorkerBusinessError(f"保存文件失败: {output_file.name}\n{str(e)}")

        # 5. 完成
        print(f"[WORKER DEBUG] Step 5: SUCCESS state")
        status_callback(TaskState.SUCCESS, "合并完成")
        print(f"[WORKER DEBUG] Sent SUCCESS status, worker done")
