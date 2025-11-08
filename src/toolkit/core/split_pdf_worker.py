# toolkit/core/split_pdf_worker.py

from pathlib import Path
from typing import Any, List
from functools import lru_cache

import pymupdf

from toolkit.i18n import gettext_text as _
from toolkit.i18n import ngettext
from toolkit.util.range_util import parse_page_ranges


def _get_page_chunks(
    total_pages: int, split_mode: str, split_value: Any
) -> List[List[int]]:
    if split_mode == "single_page":
        return [[i] for i in range(total_pages)]

    elif split_mode == "fixed_pages":
        try:
            num = int(split_value)
            if num <= 0:
                raise ValueError(_("Value must be greater than 0"))
        except Exception:
            raise ValueError(
                _("Invalid pages per file value: {split_value}").format(
                    split_value=split_value
                )
            )

        return [
            list(range(i, min(i + num, total_pages)))
            for i in range(0, total_pages, num)
        ]

    elif split_mode == "fixed_files":
        try:
            num_files = int(split_value)
            if num_files <= 0:
                raise ValueError(_("Value must be greater than 0"))

            if num_files > total_pages:
                num_files = total_pages
        except Exception:
            raise ValueError(
                _("Invalid number of files value: {split_value}").format(
                    split_value=split_value
                )
            )

        base_pages, remainder = divmod(total_pages, num_files)
        chunks: List[List[int]] = []
        current_page = 0
        for i in range(num_files):
            pages_in_this_chunk = base_pages + (1 if i < remainder else 0)
            start, end = current_page, current_page + pages_in_this_chunk
            chunks.append(list(range(start, end)))
            current_page = end
        return chunks

    elif split_mode == "custom_ranges":
        return parse_page_ranges(str(split_value), total_pages, allow_duplicates=True)

    else:
        raise ValueError(
            _("Unknown split mode: {split_mode}").format(split_mode=split_mode)
        )


@lru_cache(maxsize=10)
def get_pdf_bytes_cached(pdf_path_str):
    """获取PDF的字节内容，如果已缓存则直接返回"""
    with pymupdf.open(pdf_path_str) as doc:
        return doc.tobytes()


def split_pdf_worker(
    pdf_path,
    output_dir,
    split_mode,
    split_value,
    cancel_event,
    progress_queue,
    result_queue,
    saving_ack_event,
):
    try:
        pdf_path_obj = Path(pdf_path)
        output_folder_obj = Path(output_dir)

        with pymupdf.open(pdf_path_obj) as src_doc:
            total_pages = len(src_doc)
            if total_pages == 0:
                raise ValueError(_("PDF file is empty, no pages to split."))

            page_chunks = _get_page_chunks(total_pages, split_mode, split_value)
            total_files_to_create = len(page_chunks)
            progress_queue.put(("INIT", total_files_to_create))

            output_folder_obj.mkdir(parents=True, exist_ok=True)
            base_filename = pdf_path_obj.stem
            
            if total_files_to_create == 1:
                # 单文件输出 - 在输入文件同目录下直接创建文件
                if split_mode == "custom_ranges":
                    # 按范围命名，"R{range_str}.pdf"，","替换为"_", ":"替换为"s"
                    range_str = split_value  # 使用原始的split_value
                    safe_range_str = range_str.replace(",", "_").replace(":", "s")
                    output_name = f"{base_filename}_R{safe_range_str}.pdf"
                elif split_mode in ["fixed_pages", "fixed_files"]:
                    # 按页数/份数命名，"P{start_page_number}-{end_page_number}.pdf"
                    page_list = page_chunks[0]
                    start_page = page_list[0] + 1
                    end_page = page_list[-1] + 1
                    output_name = f"{base_filename}_P{start_page}-{end_page}.pdf"
                else:  # "single_page"
                    # 单页拆分命名，"P{page_number}.pdf"
                    page_list = page_chunks[0]
                    page_num = page_list[0] + 1
                    output_name = f"{base_filename}_P{page_num}.pdf"
                    
                output_path = output_folder_obj / output_name

                # 处理单文件输出的情况
                with pymupdf.open(stream=get_pdf_bytes_cached(str(pdf_path_obj)), filetype="pdf") as temp_doc:
                    temp_doc.select(page_chunks[0])  # 保留需要的页面
                    temp_doc.save(str(output_path), garbage=3, deflate=True)

                progress_queue.put(("PROGRESS", 1))
            else:
                # 多文件输出 - 创建以输入文件名去掉后缀的子文件夹
                subfolder_name = f"{base_filename}_{_('Split')}"
                subfolder_path = output_folder_obj / subfolder_name
                subfolder_path.mkdir(parents=True, exist_ok=True)
                
                for i, page_list in enumerate(page_chunks):
                    if cancel_event.is_set():
                        result_queue.put(("CANCEL", _("Cancelled by user.")))
                        return

                    with pymupdf.open(stream=get_pdf_bytes_cached(str(pdf_path_obj)), filetype="pdf") as temp_doc:
                        temp_doc.select(page_list)  # 保留需要的页面

                        if split_mode == "custom_ranges":
                            # 按范围命名，"R{range_str}.pdf"，","替换为"_", ":"替换为"s"
                            # 对每个chunk单独生成范围描述
                            range_parts = []
                            start_idx = 0
                            while start_idx < len(page_list):
                                # 找连续的页码段
                                end_idx = start_idx
                                while end_idx < len(page_list) - 1 and page_list[end_idx] + 1 == page_list[end_idx + 1]:
                                    end_idx += 1

                                if start_idx == end_idx:
                                    # 单个页面
                                    range_parts.append(f"P{page_list[start_idx] + 1}")
                                else:
                                    # 页面范围
                                    range_parts.append(f"P{page_list[start_idx] + 1}-{page_list[end_idx] + 1}")

                                start_idx = end_idx + 1

                            range_str = "_".join(range_parts)
                            # 替换输出文件名中的逗号为'_'，冒号为's'
                            range_str = range_str.replace(",", "_").replace(":", "s")
                            output_name = f"R{range_str}.pdf"
                        elif split_mode in ["fixed_pages", "fixed_files"]:
                            # 按页数/份数命名，"P{start_page_number}-{end_page_number}.pdf"
                            start_page = page_list[0] + 1
                            end_page = page_list[-1] + 1
                            output_name = f"P{start_page}-{end_page}.pdf"
                        else:  # "single_page"
                            # 单页拆分命名，"P{page_number}.pdf"
                            page_num = page_list[0] + 1
                            output_name = f"P{page_num}.pdf"

                        output_path = subfolder_path / output_name
                        temp_doc.save(str(output_path), garbage=3, deflate=True)

                    progress_queue.put(("PROGRESS", i + 1))

        success_msg = ngettext(
            "Split into {} PDF file.", "Split into {} PDF files.", total_files_to_create
        ).format(total_files_to_create)
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred. {}").format(e)))