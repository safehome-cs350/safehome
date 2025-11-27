#!/usr/bin/env python3

"""Main application entry point for SafeHome frontend."""

import tkinter as tk

from .login_window import LoginWindow
from .main_dashboard import MainDashboard


class SafeHomeApp:
    """Main application class for SafeHome system."""

    def __init__(self):
        """Initialize the SafeHome application."""
        self.root = tk.Tk()
        self.root.title("SafeHome System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        self.is_logged_in = False
        self.current_user = None
        self.dashboard = None

        self.show_login()

    def show_login(self):
        """Display the login window."""
        login_window = LoginWindow(self.root, self.on_login_success)
        login_window.grab_set()

    def on_login_success(self, username):
        """Handle successful login."""
        self.is_logged_in = True
        self.current_user = username
        self.show_dashboard()

    def show_dashboard(self):
        """Display the main dashboard."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.dashboard = MainDashboard(self.root, self)
        self.dashboard.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        """Log out the current user and return to login screen."""
        self.is_logged_in = False
        self.current_user = None
        self.dashboard = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.show_login()

    def update_status(self, message):
        """Update the status bar message."""
        if self.dashboard:
            self.dashboard.update_status(message)

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the application."""
    app = SafeHomeApp()
    app.run()


if __name__ == "__main__":
    main()
