import tkinter as tk
import tkinter.ttk as ttk


class ${class_name}(${base_class}):
    def __init__(self, master=None, **kw):
        super(${class_name}, self).__init__(master, **kw)
    % for call_back_name, call_back_args in call_back_list:

    def ${call_back_name}(${call_back_args}):
        pass
    % endfor


if __name__ == '__main__':
    root = tk.Tk()
% if main_widget_is_toplevel:
    widget = ${class_name}()
% else:
    widget = ${class_name}(root)
    widget.pack(expand=True, fill='both')
% endif
    root.mainloop()