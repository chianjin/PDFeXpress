from pathlib import Path


def setup_auto_output_to_parent_folder(file_list_view, output_path_picker):
    """多文件 -> 文件夹：输出路径为第一个文件的父目录"""
    first_file_var = file_list_view.get_first_file_var()

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        first_file_str = first_file_var.get()
        if not first_file_str:
            output_path_picker.path.set('')
            return

        first_file = Path(first_file_str)
        output_path_picker.set_path(first_file.parent)

    first_file_var.trace_add('write', update_output)


def setup_auto_output_with_custom_name(file_list_view, output_path_picker, name_generator):
    """多文件 -> 单文件：根据自定义规则生成输出文件名"""
    first_file_var = file_list_view.get_first_file_var()

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        first_file_str = first_file_var.get()
        if not first_file_str:
            output_path_picker.path.set('')
            return

        first_file = Path(first_file_str)
        output_name = name_generator(first_file)
        output_path = first_file.parent / output_name
        output_path_picker.set_path(output_path)

    first_file_var.trace_add('write', update_output)


def setup_auto_output_to_subfolder(file_list_view, output_path_picker):
    """多文件 -> 文件夹（子文件夹）：在第一个文件所在目录创建以其命名的子文件夹"""
    first_file_var = file_list_view.get_first_file_var()

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        first_file_str = first_file_var.get()
        if not first_file_str:
            output_path_picker.path.set('')
            return

        first_file = Path(first_file_str)
        folder_name = first_file.stem
        auto_path = first_file.parent / folder_name
        output_path_picker.set_path(auto_path)

    first_file_var.trace_add('write', update_output)


def setup_auto_output_single_file(input_path_picker, output_path_picker):
    """单文件 -> 单文件：输出路径与输入文件同目录同名（可扩展）"""
    input_path_var = input_path_picker.path

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        input_path_str = input_path_var.get()
        if not input_path_str:
            output_path_picker.path.set('')
            return

        input_path = Path(input_path_str)
        output_path_picker.set_path(input_path.parent)

    input_path_var.trace_add('write', update_output)


def setup_auto_output_single_to_folder(input_path_picker, output_path_picker):
    """单文件 -> 文件夹：输出文件夹为输入文件所在目录"""
    input_path_var = input_path_picker.path

    def update_output(*_args):
        if not output_path_picker.is_auto_output_enabled():
            return

        input_path_str = input_path_var.get()
        if not input_path_str:
            output_path_picker.path.set('')
            return

        input_path = Path(input_path_str)
        output_path_picker.set_path(input_path.parent)

    input_path_var.trace_add('write', update_output)
