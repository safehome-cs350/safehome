"""Dialog for reconfirming user identity when changing SafeHome mode."""

import tkinter as tk
from tkinter import messagebox, ttk


class ReconfirmDialog(tk.Toplevel):
    """Dialog for reconfirming user identity with address or phone number."""

    def __init__(self, parent):
        """Initialize the reconfirmation dialog.

        Args:
            parent: Parent window
        """
        super().__init__(parent)
        self.result = None
        self.address = None
        self.phone_number = None

        self.title("Reconfirm Identity")
        self.geometry("400x200")
        self.resizable(False, False)

        self.center_window()

        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main_frame,
            text=(
                "Please enter your address or phone number\nto reconfirm your identity:"
            ),
            justify=tk.LEFT,
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        ttk.Label(main_frame, text="Address:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.address_entry = ttk.Entry(main_frame, width=30)
        self.address_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.EW)

        ttk.Label(main_frame, text="Phone Number:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.phone_entry = ttk.Entry(main_frame, width=30)
        self.phone_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.EW)

        main_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ok_btn = ttk.Button(button_frame, text="OK", command=self.ok_clicked, width=12)
        ok_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(
            button_frame, text="Cancel", command=self.cancel_clicked, width=12
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        self.address_entry.focus()

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def ok_clicked(self):
        """Handle OK button click and validate input."""
        address = self.address_entry.get().strip()
        phone_number = self.phone_entry.get().strip()

        if not address and not phone_number:
            messagebox.showerror(
                "Error", "Please enter either your address or phone number"
            )
            return

        self.address = address if address else None
        self.phone_number = phone_number if phone_number else None
        self.result = True
        self.destroy()

    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = False
        self.destroy()
