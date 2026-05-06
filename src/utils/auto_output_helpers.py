from collections.abc import Callable
from pathlib import Path


def setup_auto_output_list_to_folder(
    file_list_view, output_path_picker, path_generator: Callable[[Path], Path] | None = None
):
    """
    多文件 -> 文件夹：输出路径基于第一个文件的父目录

    Args:
        file_list_view: 文件列表视图
        output_path_picker: 输出路径选择器
        path_generator: 可选的路径生成函数，接收第一个文件的Path，返回目标Path
                       如果为None，则默认使用第一个文件的父目录
    """
    first_file_var = file_list_view.get_first_file_var()

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        first_file_str = first_file_var.get()
        if not first_file_str:
            output_path_picker.path.set('')
            return

        first_file = Path(first_file_str)
        output_path = path_generator(first_file) if path_generator else first_file.parent
        output_path_picker.set_path(output_path)

    first_file_var.trace_add('write', update_output)


def setup_auto_output_list_to_single(
    file_list_view, output_path_picker, name_generator: Callable[[Path], str] | None = None
):
    """
    多文件 -> 单文件：根据自定义规则生成输出文件名

    Args:
        file_list_view: 文件列表视图
        output_path_picker: 输出路径选择器
        name_generator: 可选的文件名生成函数，接收第一个文件的Path，返回文件名字符串
                       如果为None，则默认使用原文件名
    """
    first_file_var = file_list_view.get_first_file_var()

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        first_file_str = first_file_var.get()
        if not first_file_str:
            output_path_picker.path.set('')
            return

        first_file = Path(first_file_str)
        output_name = name_generator(first_file) if name_generator else first_file.name
        output_path = first_file.parent / output_name
        output_path_picker.set_path(output_path)

    first_file_var.trace_add('write', update_output)


def setup_auto_output_single_to_single(
    input_path_picker, output_path_picker, path_generator: Callable[[Path], Path] | None = None
):
    """
    单文件 -> 单文件：输出路径与输入文件同目录

    Args:
        input_path_picker: 输入路径选择器
        output_path_picker: 输出路径选择器
        path_generator: 可选的路径生成函数，接收输入文件的Path，返回目标Path
                       如果为None，则默认使用输入文件的父目录
    """
    input_path_var = input_path_picker.path

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        input_path_str = input_path_var.get()
        if not input_path_str:
            output_path_picker.path.set('')
            return

        input_path = Path(input_path_str)
        output_path = path_generator(input_path) if path_generator else input_path.parent
        output_path_picker.set_path(output_path)

    input_path_var.trace_add('write', update_output)


def setup_auto_output_single_to_folder(
    input_path_picker, output_path_picker, path_generator: Callable[[Path], Path] | None = None
):
    """
    单文件 -> 文件夹：输出文件夹基于输入文件所在目录

    Args:
        input_path_picker: 输入路径选择器
        output_path_picker: 输出路径选择器
        path_generator: 可选的路径生成函数，接收输入文件的Path，返回目标Path
                       如果为None，则默认使用输入文件的父目录
    """
    input_path_var = input_path_picker.path

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        input_path_str = input_path_var.get()
        if not input_path_str:
            output_path_picker.path.set('')
            return

        input_path = Path(input_path_str)
        output_path = path_generator(input_path) if path_generator else input_path.parent
        output_path_picker.set_path(output_path)

    input_path_var.trace_add('write', update_output)
