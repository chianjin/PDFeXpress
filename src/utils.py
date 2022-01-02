from pathlib import Path
import tkinter as tk
from tkinter.filedialog import askopenfilenames
from tkinter.ttk import Treeview
from typing import Union

from constants import BYTE_UNIT, SCREEN_RATIO


def get_geometry(win: tk.Tk | tk.BaseWidget, screen_ratio: Union[float, tuple[int, int], None] = SCREEN_RATIO):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight() - 64

    if screen_ratio is None:
        win.update()
        wm_width = win.winfo_width()
        wm_height = win.winfo_height()
    elif type(screen_ratio) is float and screen_ratio <= 1:
        wm_width = int(screen_width * screen_ratio)
        wm_height = int(screen_height * screen_ratio)
    elif type(screen_ratio) is tuple:
        wm_width, wm_height = screen_ratio
    else:
        wm_width = 900
        wm_height = 600

    left_padding = int((screen_width - wm_width) / 2)
    top_padding = int((screen_height - wm_height) / 5)
    return f'{wm_width}x{wm_height}+{left_padding}+{top_padding}'


def int2byte_unit(value: int):
    index = 0
    while value > 1024 and index < 8:
        value /= 1024
        index += 1
    return f'{round(value)}{BYTE_UNIT[index]}B'


def add_treeview_files(treeview: Treeview, title, filetypes):
    file_list = askopenfilenames(title=title, filetypes=filetypes)
    for file in file_list:
        file_path = Path(file)
        treeview.insert('', 'end', values=(file_path.parent, file_path.name))


def move_treeview_item(treeview: Treeview, position: str):
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


def remove_treeview_items(treeview, remove_all=False):
    if remove_all:
        item_list = treeview.get_children()
    else:
        item_list = treeview.selection()
    for item in item_list:
        treeview.delete(item)


def get_treeview_files(treeview: Treeview):
    file_list = []
    for item in treeview.get_children():
        dir_name, file_name = treeview.item(item).get('values')
        file_list.append(Path(dir_name) / Path(file_name))
    return file_list
