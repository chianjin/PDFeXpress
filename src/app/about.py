import tkinter as tk
import webbrowser
from tkinter import ttk

from constant import APPLICATION_NAME, APPLICATION_VERSION, APPLICATION_URL
from utility import center_window


class About(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title(f'{_("About")} {APPLICATION_NAME}')
        self.LabelTitle = ttk.Label(self, text=APPLICATION_NAME, font='{Arial} 36 {bold}')
        self.LabelTitle.pack(side='top', padx=60, pady=40)
        self.LabelVersion = ttk.Label(self, text=APPLICATION_VERSION, font='{Arial} 14 {bold}')
        self.LabelVersion.pack()
        self.LabelURL = ttk.Label(
            self,
            text=APPLICATION_URL,
            font='{Arial} 10 {underline}',
            foreground='#0000FF',
            cursor='hand2'
        )
        self.LabelURL.pack(pady=20)
        self.LabelURL.bind('<1>', self.open_url)
        self.ButtonOK = ttk.Button(self)
        self.ButtonOK.configure(text='OK')
        self.ButtonOK.pack(pady='30')
        self.ButtonOK.configure(command=self.close)
        self.ButtonOK.focus_set()
        self.resizable(False, False)
        self.grab_set()

        center_window(self, 200)

    def open_url(self, event):
        webbrowser.open_new_tab(APPLICATION_URL)

    def close(self):
        self.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('About PDFeXpress')
    about = About(root)
    # about.pack(expand=True, fill='both', padx=4, pady=5)
    root.mainloop()
