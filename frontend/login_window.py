"""Login window for SafeHome system."""

import tkinter as tk
from tkinter import messagebox, ttk


class LoginWindow(tk.Toplevel):
    """Login window dialog."""


    def __init__(self, parent, on_success_callback):
        """Initialize the login window."""
        super().__init__(parent)
        self.on_success = on_success_callback

        self.title("SafeHome - Login")
        self.geometry("400x300")
        self.resizable(False, False)

        self.center_window()

        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame, text="SafeHome System", style="Title.TLabel"
        )
        title_label.pack(pady=(0, 30))

        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.focus()

        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.pack(pady=(0, 20))

        login_button = ttk.Button(
            main_frame, text="Login", command=self.handle_login, width=20
        )
        login_button.pack(pady=(0, 10))

        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        self.username_entry.bind(
            "<Return>", lambda e: self.password_entry.focus()
        )

        self.default_username = "admin"
        self.default_password = "admin123"

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def handle_login(self):
        """Handle login button click and validate credentials."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror(
                "Login Error", "Please enter both username and password"
            )
            return

        if (
            username == self.default_username
            and password == self.default_password
        ):
            self.destroy()
            self.on_success(username)
        else:
            messagebox.showerror("Login Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
