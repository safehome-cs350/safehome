"""Dialog for creating and editing safety zones."""

import tkinter as tk
from tkinter import messagebox, ttk


class SafetyZoneDialog(tk.Toplevel):
    """Dialog for safety zone creation and editing."""

    def __init__(self, parent, zone_data=None):
        """Initialize the safety zone dialog."""
        super().__init__(parent)
        self.result = None

        self.title("Safety Zone" if zone_data else "Create Safety Zone")
        self.geometry("400x300")
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

        ttk.Label(main_frame, text="Sensors:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        sensor_frame = ttk.Frame(main_frame)
        sensor_frame.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)

        self.sensor_listbox = tk.Listbox(
            sensor_frame, height=6, width=30, selectmode=tk.MULTIPLE
        )
        self.sensor_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(
            sensor_frame, orient=tk.VERTICAL, command=self.sensor_listbox.yview
        )
        self.sensor_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        sample_sensors = [
            "Door Sensor 1",
            "Door Sensor 2",
            "Window Sensor 1",
            "Window Sensor 2",
            "Motion Detector 1",
            "Motion Detector 2",
            "Motion Detector 3",
        ]
        for sensor in sample_sensors:
            self.sensor_listbox.insert(tk.END, sensor)

        if zone_data:
            sensors = zone_data.get("sensors", [])
            for i, sensor in enumerate(sample_sensors):
                if sensor in sensors:
                    self.sensor_listbox.selection_set(i)

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

        selected_indices = self.sensor_listbox.curselection()
        sensors = [self.sensor_listbox.get(i) for i in selected_indices]

        if not sensors:
            messagebox.showerror("Error", "Please select at least one sensor")
            return

        self.result = {
            "name": name,
            "sensors": sensors,
            "armed": False,
        }
        self.destroy()

    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.destroy()
