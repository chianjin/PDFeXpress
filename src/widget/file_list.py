import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilenames

from constant import FILE_WILDCARD
# from tktooltip import ToolTip
from utility import add_files_to_treeview


class FileList(ttk.LabelFrame):
    def __init__(self, master=None, **kw):

        super().__init__(master, **kw)
        # Treeview for filelist
        self.TreeviewFilelist = ttk.Treeview(
            master=self,
            show='headings',
            columns=('folder', 'filename'),
            selectmode='extended'
        )
        self.TreeviewFilelist.column('folder', width=100, minwidth=50, stretch=True)
        self.TreeviewFilelist.column('filename', width=300, minwidth=50, stretch=True)
        self.TreeviewFilelist.heading('folder', text=_('Folder'), anchor='w')
        self.TreeviewFilelist.heading('filename', text=_('File Name'), anchor='w')
        self.TreeviewFilelist.pack(side='left', expand=True, fill='both', padx=4, pady=4)
        # Scrollbar for filelist
        self.ScrollbarFilelist = ttk.Scrollbar(master=self, orient='vertical')
        self.ScrollbarFilelist.pack(side='left', fill='y', padx=4, pady=4)
        # Connect Treeview and Scrollbar
        self.TreeviewFilelist.configure(yscrollcommand=self.ScrollbarFilelist.set)
        self.ScrollbarFilelist.configure(command=self.TreeviewFilelist.yview)
        # Frame for command buttons
        self.FrameButton = ttk.Frame(master=self)
        # Button for add files
        self.ButtonAddFiles = ttk.Button(
            self.FrameButton,
            text=_('Add Files'),
            command=self.add_files
        )
        self.ButtonAddFiles.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonAddFiles, _('Add files.'))
        # Button for add folder
        self.ButtonAddFolder = ttk.Button(
            self.FrameButton,
            text=_('Add Folder'),
            command=self.add_folder
        )
        self.ButtonAddFolder.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonAddFiles, _('Add files from folder.'))
        # Button for remove files
        self.ButtonRemoveFiles = ttk.Button(
            self.FrameButton,
            text=_('Remove Files'),
            command=self.remove_files
        )
        self.ButtonRemoveFiles.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonRemoveFiles, _('Remove selected files.'))
        # Button for remove all
        self.ButtonRemoveAll = ttk.Button(
            self.FrameButton,
            text=_('Remove All'),
            command=self.remove_all
        )
        self.ButtonRemoveAll.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonRemoveAll, _('Remove all files.'))
        # Separator one
        self.SeparatorFile = ttk.Separator(self.FrameButton, orient='horizontal')
        self.SeparatorFile.pack(fill='x', padx=4, pady=4)
        # Button for select all
        self.ButtonSelectAll = ttk.Button(
            self.FrameButton,
            text=_('Select All'),
            command=self.select_all
        )
        self.ButtonSelectAll.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonSelectAll, _('Select all files.'))
        # Button for deselect all
        self.ButtonDeselectAll = ttk.Button(
            self.FrameButton,
            text=_('Deselect All'),
            command=self.deselect_all
        )
        self.ButtonDeselectAll.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonDeselectAll, _('Deselect all files.'))
        # Button for invert selection
        self.ButtonInvertSelection = ttk.Button(
            self.FrameButton,
            text=_('Invert Selection'),
            command=self.invert_selection
        )
        self.ButtonInvertSelection.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonInvertSelection, _('Invert selection.'))

        self.FrameButton.pack(side='left', fill='y', padx=4, pady=4)
        self.configure(text=_('PDF File List'))
        self.pack(expand=True, fill='both', padx=4, pady=4)

    def add_files(self):
        files = askopenfilenames(
            title=_('Select PDF Files'),
            filetypes=FILE_WILDCARD['pdf']
        )
        if files:
            add_files_to_treeview(self.TreeviewFilelist, files)

    def add_folder(self):
        folder = askdirectory(title=_('Select Folder'))
        if folder:
            extensions = FILE_WILDCARD['pdf'][0][1].split(';')
            file_list = []
            for ext in extensions:
                files = Path(folder).glob(ext)
                if files:
                    file_list.extend(files)
            if file_list:
                add_files_to_treeview(self.TreeviewFilelist, file_list)

    def remove_files(self):
        items = self.TreeviewFilelist.selection()
        self.TreeviewFilelist.delete(*items)

    def remove_all(self):
        items = self.TreeviewFilelist.get_children()
        self.TreeviewFilelist.delete(*items)

    def select_all(self):
        items = self.TreeviewFilelist.get_children()
        self.TreeviewFilelist.selection_set(*items)

    def deselect_all(self):
        items = self.TreeviewFilelist.get_children()
        self.TreeviewFilelist.selection_remove(*items)

    def invert_selection(self):
        items = self.TreeviewFilelist.get_children()
        selection = self.TreeviewFilelist.selection()
        deselection = set(items) - set(selection)
        self.TreeviewFilelist.selection_set(list(deselection))
        self.TreeviewFilelist.selection_remove(selection)


class FileListOrdered(FileList):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        # Separator two
        self.SeparatorMove = ttk.Separator(self.FrameButton, orient='horizontal')
        self.SeparatorMove.pack(fill='x', padx=4, pady=4)
        # Button for move to first
        self.ButtonMoveToFirst = ttk.Button(
            self.FrameButton,
            text=_('Move To First'),
            command=self.move_to_first
        )
        self.ButtonMoveToFirst.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonMoveToFirst, _('Move selected file to first.'))
        # Button for move up
        self.ButtonMoveUp = ttk.Button(
            self.FrameButton,
            text=_('Move Up'),
            command=self.move_up
        )
        self.ButtonMoveUp.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonMoveUp, _('Move up selected file.'))
        # Button for move down
        self.ButtonMoveDown = ttk.Button(
            self.FrameButton,
            text=_('Move Down'),
            command=self.move_down
        )
        self.ButtonMoveDown.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonMoveDown, _('Move down selected file.'))
        # Button for move to last
        self.ButtonMoveToLast = ttk.Button(
            self.FrameButton,
            text=_('Move To Last'),
            command=self.move_to_last
        )
        self.ButtonMoveToLast.pack(fill='x', ipadx=2, padx=4, pady=4)
        # ToolTip(self.ButtonMoveToLast, _('Move selected file to last.'))

    def add_files(self):
        files = askopenfilenames(
            title=_('Select PDF Files'),
            filetypes=FILE_WILDCARD['pdf']
        )
        if files:
            self._add_files(files)

    def add_folder(self):
        folder = askdirectory(title=_('Select Folder'))
        if folder:
            extensions = FILE_WILDCARD['pdf'][0][1].split(';')
            file_list = []
            for ext in extensions:
                files = Path(folder).glob(ext)
                if files:
                    file_list.extend(files)
            if file_list:
                file_list.sort()
                self._add_files(file_list)

    def remove_files(self):
        items = self.TreeviewFilelist.selection()
        self.TreeviewFilelist.delete(*items)

    def remove_all(self):
        items = self.TreeviewFilelist.get_children()
        self.TreeviewFilelist.delete(*items)

    def select_all(self):
        items = self.TreeviewFilelist.get_children()
        self.TreeviewFilelist.selection_set(*items)

    def deselect_all(self):
        items = self.TreeviewFilelist.get_children()
        self.TreeviewFilelist.selection_remove(*items)

    def invert_selection(self):
        items = self.TreeviewFilelist.get_children()
        selection = self.TreeviewFilelist.selection()
        deselection = set(items) - set(selection)
        self.TreeviewFilelist.selection_set(list(deselection))
        self.TreeviewFilelist.selection_remove(selection)

    def move_to_first(self):
        self._move_item('first')

    def move_up(self):
        self._move_item('up')

    def move_down(self):
        self._move_item('down')

    def move_to_last(self):
        self._move_item('last')

    def _move_item(self, position):
        items = self.TreeviewFilelist.get_children()
        item_count = len(items)
        selection = self.TreeviewFilelist.selection()
        selection_count = len(selection)
        if item_count in (0, 1) or selection_count != 1:
            return None
        selected_item = selection[0]
        index = self.TreeviewFilelist.index(selected_item)
        positions = dict(first=0, up=index - 1, down=index + 1, last='end')
        self.TreeviewFilelist.move(selected_item, '', positions[position])

    def _add_files(self, files):
        for file in files:
            index = self.TreeviewFilelist.insert('', 'end', text=file)
            self.TreeviewFilelist.set(index, 'folder', Path(file).parent)
            self.TreeviewFilelist.set(index, 'filename', Path(file).name)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('File List')
    file_list = FileListOrdered(root)
    file_list.pack(expand=True, fill='both', padx=4, pady=5)
    root.mainloop()
