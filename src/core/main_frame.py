import importlib
from tkinter import ttk

from core.not_implemented_frame import NotImplementedFrame
from feature.feature_list import FEATURE_LIST
from util.i18n import gettext_text as _
from widget.about_dialog import AboutDialog
from widget.donate_dialog import open_donate


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._loaded_feature_frame = None

        self._current_category = FEATURE_LIST[0][0][0]
        self._current_feature = FEATURE_LIST[0][1][0].feature_id

        # Left Frame
        left_frame = ttk.Frame(self)
        left_frame.pack(side='left', fill='y')
        # Feature List
        feature_list_frame = ttk.LabelFrame(left_frame, text=_('Feature List'))
        feature_list_frame.pack(expand=True, fill='y', padx=5, pady=5)

        style = ttk.Style()
        style.configure('FeatureList.Treeview', rowheight=30)

        self.treeview_menu = ttk.Treeview(
            feature_list_frame,
            show='tree',
            selectmode='browse',
            style='FeatureList.Treeview',
        )
        # self.treeview_menu.column('#0', width=150)
        self.treeview_menu.pack(side='left', fill='both', expand=1, padx=5, pady=5)

        self.treeview_menu.bind('<<TreeviewSelect>>', self._on_select)

        for (category_id, category_text), features in FEATURE_LIST:
            self.treeview_menu.insert(
                '', 'end', category_id, text=category_text, open=False
            )
            for feature in features:
                self.treeview_menu.insert(
                    category_id,
                    'end',
                    feature.feature_id,
                    text=feature.display_name,
                    values=feature,
                )
        self.treeview_menu.item(FEATURE_LIST[0][0][0], open=True)
        self.treeview_menu.selection_set(self._current_feature)

        # About Button
        ttk.Button(
            left_frame, text=_('About PDF eXpress'), command=self._on_about
        ).pack(fill='x', padx=10, pady=(0, 10))

        # Support Button
        ttk.Button(
            left_frame,
            text=_('Support Me'),
            command=lambda: open_donate(self.winfo_toplevel()),
        ).pack(fill='x', padx=10, pady=(0, 10))

        # Set Default Feature Frame
        self._load_feature_frame(self._current_feature)

    def _on_select(self, event):
        selection = self.treeview_menu.selection()
        if not selection:
            return
        selected_feature = self.treeview_menu.selection()[0]
        values = self.treeview_menu.item(selected_feature, 'values')
        if not values:
            self._set_category_open(selected_feature)
            return
        if selected_feature == self._current_feature:
            return
        self._current_feature = selected_feature
        self._load_feature_frame(selected_feature)

    def _set_category_open(self, category_id):
        self.treeview_menu.item(self._current_category, open=False)
        self._current_category = category_id
        self.treeview_menu.item(category_id, open=True)
        self.treeview_menu.selection_toggle(category_id)

    def _load_feature_frame(self, feature_id):
        _id, display_name, executive_text = self.treeview_menu.item(
            feature_id, 'values'
        )
        module_name = f'feature.{feature_id}.{feature_id}_frame'
        class_name = f'{feature_id.title().replace("_", "")}Frame'
        try:
            feature_module = importlib.import_module(module_name)
            feature_class = getattr(feature_module, class_name)
        except (ModuleNotFoundError, AttributeError):
            if self._loaded_feature_frame is not None:
                self._loaded_feature_frame.pack_forget()
            self._loaded_feature_frame = NotImplementedFrame(self, display_name)
            self._loaded_feature_frame.pack(fill='both', expand=True)
            return
        if self._loaded_feature_frame is not None:
            self._loaded_feature_frame.pack_forget()
        self._loaded_feature_frame = feature_class(self)
        self._loaded_feature_frame.pack(fill='both', expand=True)

    def _on_about(self):
        AboutDialog(self.winfo_toplevel())
