import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo

import fitz
import tkinterdnd2

from constant import FILE_WILDCARD
from utility import drop_pdf_file_to_entry
from widget import Process, FrameTitle, InputFile, OutputFile


class EditTOC(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.FrameTitle = FrameTitle(master=self, frame_title='Edit TOC')

        self.InputFile = InputFile(master=self)
        self.InputFile.input_file.trace_add('write', self.trace_input_file)
        self.TableOfContents = FrameTableOfContents(self)
        self.TableOfContents.ButtonExportTOC.configure(command=self.export_toc)

        self.OutputFile = OutputFile(self)
        self.OutputFile.configure(text=_('Output PDF File'))
        self.OutputFile.ButtonOutputFile.configure(command=self.set_output_file)

        self.Process = Process(self)
        self.Process.configure(text=_('Save'))
        self.Process.ButtonProcess.configure(text=_('Save'), command=self.save_pdf)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_file)

    def export_toc(self):
        input_file = self.InputFile.input_file.get()
        if not input_file:
            return None
        item_list = self.TableOfContents.TreeviewTableOfContents.get_children()
        if not item_list:
            return None

        initial_dir = Path(input_file).parent
        initial_file = Path(input_file).with_suffix('.txt')
        initial_file = initial_file.name
        toc_file = asksaveasfilename(
            filetypes=FILE_WILDCARD['text'],
            defaultextension='txt',
            initialdir=initial_dir,
            initialfile=initial_file
        )
        with open(toc_file, 'w') as f:
            f.write(';Page No., Level, Entry\n')
            for item in item_list:
                page_no, level, entry = self.TableOfContents.TreeviewTableOfContents.item(item)['values']
                f.write(f'{page_no}\t{level}\t{entry}\n')

    def trace_input_file(self, *args):
        input_file = self.InputFile.input_file.get()
        if input_file:
            output_file = Path(input_file)
            output_file = output_file.parent / f'{output_file.stem}-toc.pdf'
            self.OutputFile.output_file.set(output_file)
            with fitz.Document(input_file) as input_pdf:
                toc = input_pdf.get_toc()
            self.TableOfContents.TreeviewTableOfContents.delete(
                *self.TableOfContents.TreeviewTableOfContents.get_children())
            for level, entry, page_no in toc:
                self.TableOfContents.TreeviewTableOfContents.insert('', 'end', values=(page_no, level, entry))

    def set_output_file(self):
        initial_file = None
        initial_dir = None
        current_file = self.OutputFile.output_file.get()
        if current_file:
            initial_file = Path(current_file)
        else:
            input_file = self.InputFile.input_file.get()
            if input_file:
                initial_file = Path(input_file)
                initial_file = initial_file.parent / f'{initial_file.stem}-toc.pdf'
        if initial_file:
            initial_dir = initial_file.parent
        file = asksaveasfilename(
            title=_('Save PDF File'),
            filetypes=FILE_WILDCARD['pdf'],
            defaultextension='pdf',
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if file:
            self.OutputFile.output_file.set(Path(file))

    def save_pdf(self):
        if not self.OutputFile.output_file.get():
            return None
        item_list = self.TableOfContents.TreeviewTableOfContents.get_children()
        if not item_list:
            return None

        toc = []
        self.Process.ProgressBar.grab_set()
        self.Process.ProgressBar.configure(maximum=len(item_list))

        for i, item in enumerate(item_list, start=1):
            page_no, level, entry = self.TableOfContents.TreeviewTableOfContents.item(item)['values']
            toc.append((level, entry, page_no))
            self.Process.process.set(i)
        input_file = self.InputFile.input_file.get()
        with fitz.Document(input_file) as input_pdf:
            input_pdf.set_toc(toc)
            input_pdf.save(self.OutputFile.output_file.get())
        self.Process.ProgressBar.grab_release()
        showinfo(title=_('Done'), message=_('Save Completed.'))

    def drop_file(self, event):
        drop_pdf_file_to_entry(self.InputFile.input_file, event)


class FrameTableOfContents(ttk.LabelFrame):
    def __init__(self, master, *args, **kw):
        super().__init__(master, *args, **kw)

        self.configure(text=_('Table of Contents'))

        self.FrameTreeview = ttk.Frame(self)
        self.TreeviewTableOfContents = ttk.Treeview(
            master=self.FrameTreeview,
            show='headings',
            columns=('page_no', 'level', 'entry'),
        )
        self.TreeviewTableOfContents.column('page_no', width=60, stretch=False, anchor='center')
        self.TreeviewTableOfContents.column('level', width=60, stretch=False, anchor='center')
        self.TreeviewTableOfContents.column('entry', stretch=True)
        self.TreeviewTableOfContents.heading('page_no', text=_('Page No'))
        self.TreeviewTableOfContents.heading('level', text=_('Level'))
        self.TreeviewTableOfContents.heading('entry', text=_('Entry'), anchor='w')

        self.TreeviewTableOfContents.pack(side='left', expand=True, fill='both', padx=4, pady=4)
        self.TreeviewTableOfContents.bind('<<TreeviewSelect>>', self.select_item)

        self.Scrollbar = ttk.Scrollbar(self.FrameTreeview, orient='vertical')
        self.Scrollbar.pack(side='left', padx=4, pady=4, fill='y')
        self.Scrollbar.configure(command=self.TreeviewTableOfContents.yview)
        self.TreeviewTableOfContents.configure(yscrollcommand=self.Scrollbar.set)

        self.FrameButton = ttk.Frame(self.FrameTreeview)
        self.ButtonLoadTOC = ttk.Button(
            master=self.FrameButton,
            text=_('Load TOC'),
            command=self.load_toc
        )
        self.ButtonLoadTOC.pack(padx=4, pady=4)
        self.ButtonDeleteItem = ttk.Button(
            master=self.FrameButton,
            text=_('Delete Entry'),
            command=self.delete_item
        )
        self.ButtonExportTOC = ttk.Button(
            master=self.FrameButton,
            text=_('Export TOC'),
            command=self.export_toc
        )
        self.ButtonExportTOC.pack(padx=4, pady=4)
        self.ButtonDeleteItem.pack(padx=4, pady=4)
        self.ButtonDeleteAll = ttk.Button(
            master=self.FrameButton,
            text=_('Delete All'),
            command=self.delete_all
        )
        self.ButtonDeleteAll.pack(padx=4, pady=4)

        self.FrameButton.pack(side='left', fill='y', padx=4, pady=4)
        self.FrameTreeview.pack(expand=True, fill='both', padx=4, pady=4)

        self.FrameEditor = ItemEditor(self)
        self.FrameEditor.ButtonEdit.config(command=self.edit_item)

        self.pack(expand=True, fill='both', padx=4, pady=4)

    def load_toc(self):
        toc_file = askopenfilename(
            filetypes=FILE_WILDCARD['text'],
            defaultextension='txt'
        )
        if toc_file:
            self.TreeviewTableOfContents.delete(*self.TreeviewTableOfContents.get_children())
            with open(toc_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line.startswith(';'):
                        page_no, level, entry = line.split('\t')
                        self.TreeviewTableOfContents.insert('', 'end', values=(page_no, level, entry))

    def export_toc(self):
        # Defined in EditTOC
        pass

    def delete_item(self):
        self.TreeviewTableOfContents.delete(*self.TreeviewTableOfContents.selection())

    def delete_all(self):
        self.TreeviewTableOfContents.delete(*self.TreeviewTableOfContents.get_children())

    def select_item(self, event):
        items = self.TreeviewTableOfContents.selection()
        if items:
            item = items[0]
            page_no, level, entry = self.TreeviewTableOfContents.item(item)['values']
            self.FrameEditor.page_no.set(page_no)
            self.FrameEditor.level.set(level)
            self.FrameEditor.entry.set(entry)

    def edit_item(self):
        page_no = self.FrameEditor.page_no.get()
        level = self.FrameEditor.level.get()
        entry = self.FrameEditor.entry.get()

        if not (page_no and level and entry):
            return None

        item_list = self.TreeviewTableOfContents.get_children()
        page_list = [self.TreeviewTableOfContents.item(item)['values'][0] for item in item_list]

        if page_no in page_list:
            for item in item_list:
                if self.TreeviewTableOfContents.item(item)['values'][0] == page_no:
                    self.TreeviewTableOfContents.set(item, 'entry', entry)
                    self.TreeviewTableOfContents.set(item, 'level', level)
                    return None

        page_list.append(page_no)
        page_list = sorted(page_list)
        index = page_list.index(page_no)
        self.TreeviewTableOfContents.insert('', index, values=(page_no, level, entry))


class ItemEditor(tk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.page_no = tk.IntVar(value=1)
        self.level = tk.IntVar(value=1)
        self.entry = tk.StringVar()

        self.LabelPageNo = ttk.Label(self, text=_('Page No'))
        self.LabelPageNo.pack(side='left', padx=4, pady=4)
        self.EntryPageNo = ttk.Entry(self, width=5, justify='center', textvariable=self.page_no)
        self.EntryPageNo.pack(side='left', padx=4, pady=4)
        self.LabelLevel = ttk.Label(self, text=_('Level'))
        self.LabelLevel.pack(side='left', padx=4, pady=4)
        self.EntryLevel = ttk.Entry(self, width=5, justify='center', textvariable=self.level)
        self.EntryLevel.pack(side='left', padx=4, pady=4)
        self.LabelEntry = ttk.Label(self, text=_('Entry'))
        self.LabelEntry.pack(side='left', padx=4, pady=4)
        self.EntryEntry = ttk.Entry(self, textvariable=self.entry)
        self.EntryEntry.pack(side='left', padx=4, pady=4, expand=True, fill='x')
        self.ButtonEdit = ttk.Button(self, text=_('Add/Edit'))
        self.ButtonEdit.pack(side='left', padx=4, pady=4)
        self.pack(fill="x", side="top")


if __name__ == '__main__':
    root = tkinterdnd2.Tk()
    root.title(_('Edit TOC'))
    edit_toc = EditTOC(root)
    edit_toc.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
