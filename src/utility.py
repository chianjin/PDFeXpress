def center_window(window, bottom_keep=48):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight() - bottom_keep
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def get_treeview_file_list(treeview):
    file_list = []
    for item in treeview.get_children():
        file_list.append(treeview.item(item, 'text'))
    return file_list