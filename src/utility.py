import re
from pathlib import Path


def center_window(window, bottom_keep=48):
    window.update()
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight() - bottom_keep
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def add_files_to_treeview(treeview, file_list):
    for file in file_list:
        index = treeview.insert('', 'end', text=file)
        treeview.set(index, 'folder', Path(file).parent)
        treeview.set(index, 'filename', Path(file).name)


def get_treeview_file_list(treeview):
    file_list = []
    for item in treeview.get_children():
        file_list.append(treeview.item(item, 'text'))
    return file_list


def split_drop_data(data):
    file_list = []
    pattern = re.compile(r'\{([^\{\}]+)\}|(\S+)')
    for match in pattern.findall(data):
        file_name = match[0] if match[0] else match[1]
        file_name = Path(file_name)
        if file_name.is_file():
            file_list.append(file_name)
    return file_list
