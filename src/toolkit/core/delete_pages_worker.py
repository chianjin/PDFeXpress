# toolkit/core/delete_pages_worker.py

from pathlib import Path
from typing import List
from functools import lru_cache

import pymupdf

from toolkit.i18n import gettext_text as _
from toolkit.i18n import ngettext
from toolkit.util.range_util import parse_page_ranges


def delete_pages_worker(
    pdf_path,
    output_dir,
    pages_to_delete_str,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        if not pages_to_delete_str:
            raise ValueError(_("No pages specified to delete."))

        with pymupdf.open(pdf_path) as doc:
            total_pages_doc = len(doc)
            if total_pages_doc == 0:
                raise ValueError(_("PDF file has no pages."))

            # 解析多组删除范围，不允许重复
            delete_groups = parse_page_ranges(pages_to_delete_str, total_pages_doc, allow_duplicates=False)
            
            if not delete_groups:
                raise ValueError(
                    _(
                        "No valid pages could be parsed from '{pages_to_delete_str}'."
                    ).format(pages_to_delete_str=pages_to_delete_str)
                )

            # 处理多组删除，需要创建子文件夹并保存多个文件
            pdf_path_obj = Path(pdf_path)
            base_filename = pdf_path_obj.stem
            output_dir_obj = Path(output_dir)
            
            # 创建输出子文件夹
            subfolder_name = f"{base_filename}_{_('Deleted')}"
            subfolder_path = output_dir_obj / subfolder_name
            subfolder_path.mkdir(parents=True, exist_ok=True)
            
            progress_queue.put(("INIT", len(delete_groups)))

            # 使用缓存避免重复读取原PDF
            src_doc_bytes = get_pdf_bytes_cached(str(pdf_path))
            
            for i, pages_to_delete_list in enumerate(delete_groups):
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return

                # 将删除列表转换为集合，确保唯一性
                pages_to_delete_set = set(pages_to_delete_list)
                
                # 计算要保留的页面
                pages_to_keep = [
                    p for p in range(total_pages_doc) if p not in pages_to_delete_set
                ]
                if not pages_to_keep:
                    raise ValueError(
                        _("Will delete all pages from {pdf_path_name} in group {group_num}.").format(
                            pdf_path_name=pdf_path_obj.name, group_num=i+1
                        )
                    )

                # 使用缓存的文档创建新文档
                with pymupdf.open(stream=src_doc_bytes, filetype="pdf") as new_doc:
                    new_doc.select(pages_to_keep)

                    # 根据删除的页面范围生成文件名
                    delete_list = sorted(list(pages_to_delete_set))
                    range_parts = []
                    start_idx = 0
                    while start_idx < len(delete_list):
                        # 找连续的页码段
                        end_idx = start_idx
                        while end_idx < len(delete_list) - 1 and delete_list[end_idx] + 1 == delete_list[end_idx + 1]:
                            end_idx += 1

                        if start_idx == end_idx:
                            # 单个页面
                            range_parts.append(f"P{delete_list[start_idx] + 1}")
                        else:
                            # 页面范围
                            range_parts.append(f"P{delete_list[start_idx] + 1}-{delete_list[end_idx] + 1}")

                        start_idx = end_idx + 1

                    range_str = "_".join(range_parts)
                    # 替换输出文件名中的逗号为'_'，冒号为's'（虽然删除范围中不会有这些字符，但为了一致性）
                    range_str = range_str.replace(",", "_").replace(":", "s")
                    output_name = f"R{range_str}.pdf"

                    output_file_path = subfolder_path / output_name
                    new_doc.save(str(output_file_path), garbage=4, deflate=True)

                progress_queue.put(("PROGRESS", i + 1))

            success_msg = ngettext(
                "Deleted pages in {} PDF file.", "Deleted pages in {} PDF files.", len(delete_groups)
            ).format(len(delete_groups))
            result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))


@lru_cache(maxsize=10)
def get_pdf_bytes_cached(pdf_path_str):
    """获取PDF的字节内容，如果已缓存则直接返回"""
    with pymupdf.open(pdf_path_str) as doc:
        return doc.tobytes()