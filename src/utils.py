import re
from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames
from tkinter.messagebox import showerror
from tkinter.ttk import Treeview

import fitz

from constants import BYTE_UNIT, FILE_TYPES_PDF


def int2byte_unit(value: int):
    index = 0
    while value > 1024 and index < 8:
        value /= 1024
        index += 1
    return f'{round(value)}{BYTE_UNIT[index]}B'


def pdf_info(pdf_file):
    page_count = 0
    with fitz.Document(pdf_file) as pdf:
        page_count = pdf.page_count
    pdf_file = Path(pdf_file)
    return pdf_file, page_count, len(str(page_count))


def get_pdf_info(title=_('Select PDF file'), filetypes=FILE_TYPES_PDF):
    pdf_file = askopenfilename(title=title, filetypes=filetypes)
    if pdf_file:
        return pdf_info(pdf_file)


def check_file_exist(file_path: Path):
    if not file_path.exists():
        showerror(
                title=_('File not exist.'),
                message=_('{}\nFile not exist, please check.').format(file_path)
                )
        return False
    return True


def check_dir(dir_path: Path):
    if not dir_path.exists():
        dir_path.mkdir()


def treeview_add_files(treeview: Treeview, title, filetypes):
    file_list = askopenfilenames(title=title, filetypes=filetypes)
    for file in file_list:
        file_path = Path(file)
        treeview.insert('', 'end', text=file_path, values=(file_path.parent, file_path.name))


def treeview_move_item(treeview: Treeview, position: str):
    item_list = treeview.get_children()
    item_count = len(item_list)
    selected_list = treeview.selection()
    selected_count = len(selected_list)
    if item_count == 1 or selected_count != 1:
        return None
    selected_item = selected_list[0]
    index = item_list.index(selected_item)
    if position == 'top':
        new_index = 0
    elif position == 'bottom':
        new_index = 'end'
    elif position == 'up':
        new_index = index - 1
    elif position == 'down':
        new_index = index + 1
    else:
        return None
    treeview.move(selected_item, '', new_index)


def treeview_remove_items(treeview, remove_all=False):
    if remove_all:
        item_list = treeview.get_children()
    else:
        item_list = treeview.selection()
    treeview.delete(*item_list)


def treeview_get_file_list(treeview: Treeview):
    file_list = []
    for item in treeview.get_children():
        file_path = treeview.item(item, 'text')
        file_list.append(Path(file_path))
    return file_list


def treeview_get_first_file(treeview: Treeview):
    file_list = treeview_get_file_list(treeview)
    if file_list:
        return file_list[0]
    else:
        return ''


def split_drop_data(data):
    file_list = []
    pattern = re.compile(r'\{([^\{\}]+)\}|(\S+)')
    for match in pattern.findall(data):
        file_name = match[0] if match[0] else match[1]
        file_name = Path(file_name)
        if file_name.is_file():
            file_list.append(file_name)
    return file_list


def treeview_drop_files(treeview, file_list: list[Path], file_type):
    for file in file_list:
        if file.suffix.lower() in file_type[0][1]:
            treeview.insert('', 'end', text=file, values=(file.parent, file.name))
