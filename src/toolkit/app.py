# src/toolkit/app.py
import tkinter as tk
from tkinter import ttk

# 相对导入 i18n 和各个"迷你应用"
from toolkit.i18n import gettext_text as _
from toolkit.ui.feature.to_image import PdfToImageApp
from toolkit.ui.feature.merge import MergePdfApp
from toolkit.ui.feature.image_to_pdf import ImageToPdfApp

class MultiApp(ttk.Frame):
    """    组合应用。
    这个类是一个"笨"容器。
    它只负责创建 Notebook，并把"迷你应用"作为选项卡放进去。
    """
    def __init__(self, root):
        super().__init__(root, padding="10")
        self.root = root
        self.root.title(_("Multifunctional PDF Toolkit"))
        self.root.geometry("500x500")
        self.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建"迷你应用"实例
        # 它们现在是自包含的，不需要传递 'app_controller'
        self.tab1 = PdfToImageApp(self.notebook)
        self.tab2 = MergePdfApp(self.notebook)
        self.tab3 = ImageToPdfApp(self.notebook)

        # 添加到 Notebook
        self.notebook.add(self.tab1, text=_("PDF to Image"))
        self.notebook.add(self.tab2, text=_("Merge PDF"))
        self.notebook.add(self.tab3, text=_("Image to PDF"))