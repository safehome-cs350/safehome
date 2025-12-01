"""Dialog for displaying system notifications."""

import tkinter as tk
from tkinter import ttk


class NotificationDialog(tk.Toplevel):
    """Dialog for displaying system notifications."""

    def __init__(self, parent, title, message):
        """Initialize the notification dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Notification message to display
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("500x200")
        self.resizable(False, False)

        self.center_window()

        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))

        # Message label
        message_label = ttk.Label(
            main_frame, text=message, font=("Arial", 11), wraplength=450
        )
        message_label.pack(pady=10)

        # OK button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        ok_btn = ttk.Button(button_frame, text="OK", command=self.ok_clicked, width=15)
        ok_btn.pack()

        # Make window stay on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def ok_clicked(self):
        """Handle OK button click."""
        self.destroy()
