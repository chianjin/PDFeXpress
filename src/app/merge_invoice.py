from pathlib import Path
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo

import fitz
import tkinterdnd2

from constant import FILE_WILDCARD, BASE_FOLDER
from utility import get_treeview_file_list, drop_pdf_files_to_treeview
from widget import FileList, OutputFile, Process, FrameTitle

BLANK_PDF = BASE_FOLDER / 'data/blank.pdf'
LIMITED_HEIGHT = 397  # 14 * 72 / 2.54 = 396.8504
INVOICE_HEIGHT = 14 * 72 / 2.54  # 14cm
A4_WIDTH = 21 * 72 / 2.54  # 21cm
A4_HEIGHT = 29.7 * 72 / 2.54  # 29.7cm
A4_RECT = fitz.Rect(0, 0, A4_WIDTH, A4_HEIGHT)
UP_RECT = fitz.Rect(0, 0, A4_WIDTH, INVOICE_HEIGHT)
DOWN_RECT = fitz.Rect(0, INVOICE_HEIGHT, A4_WIDTH, INVOICE_HEIGHT * 2)


class MergeInvoice(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        self.FrameTitle = FrameTitle(master=self, frame_title=_('Merge Invoice'))
        self.FrameTitle.pack(fill='x', padx=4, pady=4)

        self.FileList = FileList(master=self)
        self.FileList.configure(text=_('Invoice File List'))

        self.OutputFile = OutputFile(master=self)
        self.OutputFile.configure(text=_('PDF Output File'))
        self.OutputFile.ButtonOutputFile.configure(command=self.set_output_file)

        self.Process = Process(master=self)
        self.Process.configure(text=_('Merge Invoice'))
        self.Process.ButtonProcess.configure(text=_('Merge'), command=self.merge_invoice)

        self.drop_target_register(tkinterdnd2.DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        drop_pdf_files_to_treeview(self.FileList.TreeviewFilelist, event)

    def set_output_file(self):
        initial_dir = None
        initial_file = None
        current_file = self.OutputFile.output_file.get()
        if current_file:
            initial_dir = Path(current_file).parent
            initial_file = Path(current_file).name
        else:
            item_list = self.FileList.TreeviewFilelist.get_children()
            if item_list:
                current_file = self.FileList.TreeviewFilelist.item(item_list[0])['text']
                initial_dir = Path(current_file).parent.parent
                initial_file = f'{Path(current_file).parent.name}-merged_invoice.pdf'
        file = asksaveasfilename(
            title=_('Select PDF Output File'),
            filetypes=FILE_WILDCARD['pdf'],
            defaultextension='.pdf',
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if file:
            self.OutputFile.output_file.set(Path(file))

    def merge_invoice(self):
        file_list = get_treeview_file_list(self.FileList.TreeviewFilelist)
        if len(file_list) < 2:
            return None
        output_file = self.OutputFile.output_file.get()
        if not output_file:
            return None

        self.Process.ProgressBar.grab_set()
        self.Process.process.set(0)
        self.Process.ProgressBar.configure(maximum=len(file_list))

        normal_invoices, other_invoices = self._get_invoices_list(file_list)
        merged_normal_pdf = fitz.Document()
        merged_other_pdf = fitz.Document()
        blank_pdf = fitz.Document(BLANK_PDF)
        count = 0
        for file in other_invoices:
            other_pdf = fitz.Document(file)
            for pno in range(other_pdf.page_count):
                new_page = merged_other_pdf.new_page(width=A4_WIDTH, height=A4_HEIGHT)
                other_page = other_pdf.load_page(pno)
                new_page.show_pdf_page(other_page.rect, other_pdf, pno)
            other_pdf.close()
            count += 1
            self.Process.process.set(count)
            self.Process.ProgressBar.update_idletasks()
        for i in range(0, len(normal_invoices), 2):
            new_page = merged_normal_pdf.new_page(width=A4_WIDTH, height=A4_HEIGHT)
            new_page.show_pdf_page(A4_RECT, blank_pdf, 0)
            up_pdf = fitz.Document(normal_invoices[i])
            new_page.show_pdf_page(UP_RECT, up_pdf, 0)
            up_pdf.close()
            count += 1
            self.Process.process.set(count)
            self.Process.ProgressBar.update_idletasks()
            try:
                down_pdf = fitz.Document(normal_invoices[i + 1])
                new_page.show_pdf_page(DOWN_RECT, down_pdf, 0)
                down_pdf.close()
                count += 1
                self.Process.process.set(count)
                self.Process.ProgressBar.update_idletasks()
            except:
                pass
        if merged_other_pdf.page_count > 0:
            merged_normal_pdf.insert_pdf(merged_other_pdf)
        merged_other_pdf.close()
        merged_normal_pdf.save(output_file, garbage=4, deflate=True)
        merged_normal_pdf.close()
        blank_pdf.close()
        self.Process.ProgressBar.grab_release()
        showinfo(title=_('Done'), message=_('Merge Completed.'))
        self.Process.process.set(0)

    def _get_invoices_list(self, file_list):
        normal_invoices = []
        other_invoices = []
        for file in file_list:
            if self._is_normal_invoice(file):
                normal_invoices.append(file)
            else:
                other_invoices.append(file)
        return normal_invoices, other_invoices

    def _is_normal_invoice(self, file):
        pdf = fitz.Document(file)
        if pdf.page_count != 1:
            pdf.close()
            return False
        page = pdf.load_page(0)
        if page.rect.height > LIMITED_HEIGHT:
            pdf.close()
            return False
        return True


if __name__ == '__main__':
    root = tkinterdnd2.Tk()
    root.title('Merge PDF')
    merge_pdf = MergeInvoice(root)
    merge_pdf.pack(expand=True, fill='both', padx=4, pady=4)
    root.mainloop()
