import tkinter as tk
from tkinter import ttk

from .configuration_panel import ConfigurationPanel
from .security_panel import SecurityPanel
from .surveillance_panel import SurveillancePanel


class MainDashboard(ttk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.setup_ui()

    def setup_ui(self):
        self.create_menu_bar()
        self.create_content_area()
        self.create_status_bar()

    def create_menu_bar(self):
        menu_frame = ttk.Frame(self)
        menu_frame.pack(fill=tk.X, padx=5, pady=5)

        title_label = ttk.Label(menu_frame, text="SafeHome", font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)

        nav_frame = ttk.Frame(menu_frame)
        nav_frame.pack(side=tk.LEFT, padx=20)

        self.security_btn = ttk.Button(
            nav_frame,
            text="Security",
            command=lambda: self.show_panel("security"),
            width=15,
        )
        self.security_btn.pack(side=tk.LEFT, padx=5)

        self.surveillance_btn = ttk.Button(
            nav_frame,
            text="Surveillance",
            command=lambda: self.show_panel("surveillance"),
            width=15,
        )
        self.surveillance_btn.pack(side=tk.LEFT, padx=5)

        self.config_btn = ttk.Button(
            nav_frame,
            text="Configuration",
            command=lambda: self.show_panel("configuration"),
            width=15,
        )
        self.config_btn.pack(side=tk.LEFT, padx=5)

        user_frame = ttk.Frame(menu_frame)
        user_frame.pack(side=tk.RIGHT, padx=10)

        user_label = ttk.Label(user_frame, text=f"User: {self.app.current_user}", font=("Arial", 10))
        user_label.pack(side=tk.LEFT, padx=5)

        logout_btn = ttk.Button(user_frame, text="Logout", command=self.app.logout, width=10)
        logout_btn.pack(side=tk.LEFT, padx=5)

    def create_content_area(self):
        self.content_notebook = ttk.Notebook(self)
        self.content_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.security_panel = SecurityPanel(self.content_notebook, self.app)
        self.content_notebook.add(self.security_panel, text="Security")

        self.surveillance_panel = SurveillancePanel(self.content_notebook, self.app)
        self.content_notebook.add(self.surveillance_panel, text="Surveillance")

        self.config_panel = ConfigurationPanel(self.content_notebook, self.app)
        self.content_notebook.add(self.config_panel, text="Configuration")

        self.content_notebook.select(0)

    def create_status_bar(self):
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        self.status_label = ttk.Label(status_frame, text="System Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def show_panel(self, panel_name):
        panel_map = {
            "security": 0,
            "surveillance": 1,
            "configuration": 2,
        }
        if panel_name in panel_map:
            self.content_notebook.select(panel_map[panel_name])

    def update_status(self, message):
        self.status_label.config(text=message)
