#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk

from .login_window import LoginWindow
from .main_dashboard import MainDashboard


class SafeHomeApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SafeHome System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        self.is_logged_in = False
        self.current_user = None
        self.dashboard = None

        self.show_login()

    def show_login(self):
        login_window = LoginWindow(self.root, self.on_login_success)
        login_window.grab_set()

    def on_login_success(self, username):
        self.is_logged_in = True
        self.current_user = username
        self.show_dashboard()

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.dashboard = MainDashboard(self.root, self)
        self.dashboard.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        self.is_logged_in = False
        self.current_user = None
        self.dashboard = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.show_login()

    def update_status(self, message):
        if self.dashboard:
            self.dashboard.update_status(message)

    def run(self):
        self.root.mainloop()


def main():
    app = SafeHomeApp()
    app.run()


if __name__ == "__main__":
    main()
