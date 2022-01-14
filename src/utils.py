from pathlib import Path
from tkinter import BaseWidget, Tk
from tkinter.filedialog import askopenfilename, askopenfilenames
from tkinter.messagebox import showerror
from tkinter.ttk import Treeview
from typing import Union, Tuple

import fitz

from constants import BYTE_UNIT, FILE_TYPES_PDF, SCREEN_RATIO


def int2byte_unit(value: int):
    index = 0
    while value > 1024 and index < 8:
        value /= 1024
        index += 1
    return f'{round(value)}{BYTE_UNIT[index]}B'


def get_geometry(win: Union[Tk, BaseWidget], screen_ratio: Union[float, Tuple[int], None] = SCREEN_RATIO):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight() - 64

    if screen_ratio is None:
        win.update()
        wm_width = win.winfo_width()
        wm_height = win.winfo_height()
    elif type(screen_ratio) is float and screen_ratio <= 1:
        wm_width = int(screen_width * screen_ratio)
        wm_height = int(wm_width / 3 * 2)
        # wm_height = int(screen_height * screen_ratio)
    elif type(screen_ratio) is tuple:
        wm_width, wm_height = screen_ratio
    else:
        wm_width = 900
        wm_height = 600

    left_padding = int((screen_width - wm_width) / 2)
    top_padding = int((screen_height - wm_height) / 5)
    return f'{wm_width}x{wm_height}+{left_padding}+{top_padding}'


def get_pdf_info(title=_('Select PDF file'), filetypes=FILE_TYPES_PDF):
    page_count = 0
    pdf_file = askopenfilename(title=title, filetypes=filetypes)
    if pdf_file:
        with fitz.Document(pdf_file) as pdf:
            page_count = pdf.page_count
        pdf_file = Path(pdf_file)
    return pdf_file, page_count, len(str(page_count))


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
        treeview.insert('', 'end', values=(file_path.parent, file_path.name))


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
        new_index = index + 2
    else:
        return None
    values = treeview.item(selected_item).get('values')
    inserted_item = treeview.insert('', new_index, values=values)
    treeview.delete(selected_item)
    treeview.selection_set(inserted_item)


def treeview_remove_items(treeview, remove_all=False):
    if remove_all:
        item_list = treeview.get_children()
    else:
        item_list = treeview.selection()
    for item in item_list:
        treeview.delete(item)


def treeview_get_file_list(treeview: Treeview):
    file_list = []
    for item in treeview.get_children():
        dir_name, file_name = treeview.item(item).get('values')
        file_list.append(Path(dir_name) / Path(file_name))
    return file_list


def treeview_get_first_file(treeview: Treeview):
    item_list = treeview.get_children()
    item_count = len(item_list)
    if item_count > 0:
        dir_name, file_name = treeview.item(item_list[0]).get('values')
        return Path(dir_name) / Path(file_name)
    else:
        return ''
