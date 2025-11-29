"""Dialog for creating and editing safety zones."""

import tkinter as tk
from tkinter import messagebox, ttk


class SafetyZoneDialog(tk.Toplevel):
    """Dialog for safety zone creation and editing."""

    def __init__(self, parent, zone_data=None, available_devices=None):
        """Initialize the safety zone dialog.

        Args:
            parent: Parent window
            zone_data: Existing zone data dict with 'name' and 'device_ids' keys
            available_devices: List of device dicts with 'id' and 'type' keys
        """
        super().__init__(parent)
        self.result = None
        self.available_devices = available_devices or []

        self.title("Edit Safety Zone" if zone_data else "Create Safety Zone")
        self.geometry("400x350")
        self.resizable(False, False)

        self.center_window()

        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Zone Name:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)
        if zone_data:
            self.name_entry.insert(0, zone_data.get("name", ""))

        ttk.Label(main_frame, text="Devices:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        device_frame = ttk.Frame(main_frame)
        device_frame.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)

        self.device_listbox = tk.Listbox(
            device_frame, height=8, width=30, selectmode=tk.MULTIPLE
        )
        self.device_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(
            device_frame, orient=tk.VERTICAL, command=self.device_listbox.yview
        )
        self.device_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate device listbox
        for device in self.available_devices:
            device_id = device.get("id", "")
            device_type = device.get("type", "")
            display_text = f"Device {device_id} ({device_type})"
            self.device_listbox.insert(tk.END, display_text)

        # Store device IDs for each listbox item
        self.device_ids = [device.get("id") for device in self.available_devices]

        # Select devices if editing existing zone
        if zone_data:
            existing_device_ids = zone_data.get("device_ids", [])
            for i, device_id in enumerate(self.device_ids):
                if device_id in existing_device_ids:
                    self.device_listbox.selection_set(i)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ok_btn = ttk.Button(button_frame, text="OK", command=self.ok_clicked, width=12)
        ok_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(
            button_frame, text="Cancel", command=self.cancel_clicked, width=12
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        self.name_entry.focus()

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
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a zone name")
            return

        selected_indices = self.device_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one device")
            return

        # Get device IDs for selected devices
        selected_device_ids = [self.device_ids[i] for i in selected_indices]

        self.result = {
            "name": name,
            "device_ids": selected_device_ids,
        }
        self.destroy()

    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.destroy()
