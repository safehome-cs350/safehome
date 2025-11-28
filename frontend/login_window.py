"""Login window for SafeHome system."""

import tkinter as tk
from tkinter import messagebox, ttk

from .api_client import APIClient


class LoginWindow(tk.Toplevel):
    """Login window dialog."""

    def __init__(self, parent, on_success_callback):
        """Initialize the login window."""
        super().__init__(parent)
        self.on_success = on_success_callback
        self.api_client = APIClient()

        self.title("SafeHome - Login")
        self.geometry("400x400")
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

        ttk.Label(main_frame, text="User ID:").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.focus()

        ttk.Label(main_frame, text="Password 1:").pack(anchor=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password_entry.pack(pady=(0, 15))

        ttk.Label(main_frame, text="Password 2:").pack(anchor=tk.W, pady=(0, 5))
        self.password2_entry = ttk.Entry(main_frame, width=30, show="*")
        self.password2_entry.pack(pady=(0, 20))

        login_button = ttk.Button(
            main_frame, text="Login", command=self.handle_login, width=20
        )
        login_button.pack(pady=(0, 10))

        self.password_entry.bind("<Return>", lambda e: self.password2_entry.focus())
        self.password2_entry.bind("<Return>", lambda e: self.handle_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

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
        user_id = self.username_entry.get().strip()
        password1 = self.password_entry.get().strip()
        password2 = self.password2_entry.get().strip()

        if not user_id or not password1 or not password2:
            messagebox.showerror(
                "Login Error", "Please enter user ID and both passwords"
            )
            return

        try:
            self.api_client.login(user_id, password1, password2)
            self.destroy()
            self.on_success(user_id)
        except Exception as e:
            error_message = str(e)
            if "401" in error_message:
                error_message = "Invalid user ID or password"
            elif "Connection" in error_message or "refused" in error_message.lower():
                error_message = (
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running."
                )
            else:
                error_message = f"Login failed: {error_message}"
            messagebox.showerror("Login Error", error_message)
            self.password_entry.delete(0, tk.END)
            self.password2_entry.delete(0, tk.END)
