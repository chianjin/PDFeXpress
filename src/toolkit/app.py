import tkinter as tk
from tkinter import ttk, messagebox

# 相对导入 i18n 和各个"迷你应用"
from toolkit.i18n import gettext_text as _
from toolkit.ui.feature.image_to_pdf import ImageToPdfApp
from toolkit.ui.feature.merge_pdf import MergePdfApp


# from toolkit.ui.feature.to_image import PdfToImageApp # 暂时不注册

class MainFrame(ttk.Frame):  # 保持类名为 MainFrame
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)  # 确保 MainFrame 填充整个父容器

        # Main layout uses grid for fixed sidebar and expanding content
        self.columnconfigure(1, weight=1)  # Column for content frame expands
        self.rowconfigure(0, weight=1)  # Row for both frames expands

        # Left Navigation Frame
        self.nav_frame = ttk.LabelFrame(self, text=_("Operation"))
        self.nav_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=5)
        self.nav_frame.columnconfigure(0, weight=1)
        self.nav_frame.pack_propagate(False)  # Prevent frame from resizing to fit contents

        # Right Content Frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky="nswe")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        self.current_app_frame = None
        self.app_instances = {}
        self.nav_buttons = {}  # 初始化 nav_buttons 字典

        self.button_row_counter = 0  # To keep track of button rows

        # Navigation Buttons
        self._create_nav_button(_("Merge PDF"), MergePdfApp)
        self._create_nav_button(_("Image to PDF"), ImageToPdfApp)
        self._create_nav_button(_("Split PDF"), None)  # Placeholder
        self._create_nav_button(_("Rotate PDF"), None)  # Placeholder
        # Add more buttons here for other applications

        # Initially display the Merge PDF app
        self._show_app(MergePdfApp)

    def _create_nav_button(self, text: str, app_class):
        button = ttk.Button(self.nav_frame, text=text, command=lambda ac=app_class: self._show_app(ac))
        button.grid(row=self.button_row_counter, column=0, sticky="ew", pady=(5, 0), padx=5)
        self.nav_buttons[app_class] = button  # 存储按钮实例以便更新状态
        self.button_row_counter += 1

    def _show_app(self, app_class):
        if app_class is None:
            messagebox.showinfo(_("Coming Soon"), _("This feature is not yet implemented."))
            return

        # 隐藏当前 app frame
        if self.current_app_frame:
            self.current_app_frame.pack_forget()

        # 获取或创建 app 实例
        if app_class not in self.app_instances:
            self.app_instances[app_class] = app_class(self.content_frame)

        self.current_app_frame = self.app_instances[app_class]
        self.current_app_frame.pack(expand=True, fill="both")

        # 更新导航按钮状态
        for ac, button in self.nav_buttons.items():
            if ac == app_class:
                button.state(['disabled'])
            else:
                button.state(['!disabled'])


if __name__ == "__main__":
    import tkinterdnd2

    root = tkinterdnd2.Tk()
    root.title(_("PDF Toolbox Debug"))
    root.geometry("1280x768")
    app = MainFrame(root)
    root.mainloop()
