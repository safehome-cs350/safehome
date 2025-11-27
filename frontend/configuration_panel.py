"""Configuration panel for system settings."""

import tkinter as tk
from tkinter import messagebox, ttk


class ConfigurationPanel(ttk.Frame):
    """Panel for system configuration and settings."""


    def __init__(self, parent, app):
        """Initialize the configuration panel."""
        super().__init__(parent)
        self.app = app

        self.settings = {
            "master_password": "admin123",
            "guest_password": "guest123",
            "delay_time": 30,
            "phone_number": "555-0100",
            "system_name": "SafeHome System",
        }

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        settings_frame = ttk.LabelFrame(
            main_frame, text="System Settings", padding=15
        )
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        row = 0
        ttk.Label(settings_frame, text="System Name:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.system_name_var = tk.StringVar(value=self.settings["system_name"])
        ttk.Entry(
            settings_frame, textvariable=self.system_name_var, width=30
        ).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        row += 1
        ttk.Label(settings_frame, text="Master Password:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        password_frame = ttk.Frame(settings_frame)
        password_frame.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        self.master_password_var = tk.StringVar(value="********")
        self.master_password_entry = ttk.Entry(
            password_frame,
            textvariable=self.master_password_var,
            width=25,
            show="*",
        )
        self.master_password_entry.pack(side=tk.LEFT)

        change_btn = ttk.Button(
            password_frame,
            text="Change",
            command=self.change_master_password,
            width=10,
        )
        change_btn.pack(side=tk.LEFT, padx=5)

        row += 1
        ttk.Label(settings_frame, text="Guest Password:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        guest_password_frame = ttk.Frame(settings_frame)
        guest_password_frame.grid(
            row=row, column=1, pady=5, padx=5, sticky=tk.W
        )

        self.guest_password_var = tk.StringVar(value="********")
        self.guest_password_entry = ttk.Entry(
            guest_password_frame,
            textvariable=self.guest_password_var,
            width=25,
            show="*",
        )
        self.guest_password_entry.pack(side=tk.LEFT)

        change_guest_btn = ttk.Button(
            guest_password_frame,
            text="Change",
            command=self.change_guest_password,
            width=10,
        )
        change_guest_btn.pack(side=tk.LEFT, padx=5)

        row += 1
        ttk.Label(settings_frame, text="Delay Time (seconds):").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.delay_time_var = tk.StringVar(
            value=str(self.settings["delay_time"])
        )
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        ttk.Entry(delay_frame, textvariable=self.delay_time_var, width=10).pack(
            side=tk.LEFT
        )
        ttk.Label(delay_frame, text="(Time before alarm triggers)").pack(
            side=tk.LEFT, padx=5
        )

        row += 1
        ttk.Label(settings_frame, text="Monitoring Phone:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.phone_number_var = tk.StringVar(
            value=self.settings["phone_number"]
        )
        ttk.Entry(
            settings_frame, textvariable=self.phone_number_var, width=30
        ).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        control_frame = ttk.LabelFrame(
            main_frame, text="System Control", padding=15
        )
        control_frame.pack(fill=tk.X, pady=10)

        system_control_frame = ttk.Frame(control_frame)
        system_control_frame.pack(fill=tk.X, pady=5)

        ttk.Label(system_control_frame, text="System Power:").pack(
            side=tk.LEFT, padx=5
        )
        self.system_power_var = tk.StringVar(value="ON")
        power_status_label = ttk.Label(
            system_control_frame,
            textvariable=self.system_power_var,
            font=("Arial", 10, "bold"),
        )
        power_status_label.pack(side=tk.LEFT, padx=10)

        turn_on_btn = ttk.Button(
            system_control_frame,
            text="Turn On",
            command=self.turn_system_on,
            width=12,
        )
        turn_on_btn.pack(side=tk.LEFT, padx=5)
        turn_off_btn = ttk.Button(
            system_control_frame,
            text="Turn Off",
            command=self.turn_system_off,
            width=12,
        )
        turn_off_btn.pack(side=tk.LEFT, padx=5)

        reset_frame = ttk.Frame(control_frame)
        reset_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            reset_frame,
            text="Reset System:",
            font=("Arial", 10),
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(
            reset_frame,
            text="This will reset all system settings to defaults",
            foreground="gray",
        ).pack(side=tk.LEFT, padx=5)

        reset_btn = ttk.Button(
            reset_frame,
            text="Reset System",
            command=self.reset_system,
            width=15,
        )
        reset_btn.pack(side=tk.RIGHT, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        save_btn = ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=20,
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(
            button_frame, text="Cancel", command=self.cancel_changes, width=20
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def change_master_password(self):
        """Open dialog to change master password."""
        dialog = PasswordChangeDialog(self, "Master Password")
        if dialog.result:
            self.settings["master_password"] = dialog.result
            messagebox.showinfo(
                "Success", "Master password changed successfully"
            )

    def change_guest_password(self):
        """Open dialog to change guest password."""
        dialog = PasswordChangeDialog(self, "Guest Password")
        if dialog.result:
            self.settings["guest_password"] = dialog.result
            messagebox.showinfo(
                "Success", "Guest password changed successfully"
            )

    def turn_system_on(self):
        """Turn the system on."""
        result = messagebox.askyesno(
            "Turn System On", "Are you sure you want to turn the system on?"
        )
        if result:
            self.system_power_var.set("ON")
            messagebox.showinfo("Success", "System turned on")
            self.app.update_status("System turned on")

    def turn_system_off(self):
        """Turn the system off."""
        result = messagebox.askyesno(
            "Turn System Off", "Are you sure you want to turn the system off?"
        )
        if result:
            self.system_power_var.set("OFF")
            messagebox.showinfo("Success", "System turned off")
            self.app.update_status("System turned off")

    def reset_system(self):
        """Reset system to default settings."""
        result = messagebox.askyesno(
            "Reset System",
            "This will reset all system settings to defaults. Are you sure?",
        )
        if result:
            self.settings = {
                "master_password": "admin123",
                "guest_password": "guest123",
                "delay_time": 30,
                "phone_number": "555-0100",
                "system_name": "SafeHome System",
            }

            self.system_name_var.set(self.settings["system_name"])
            self.delay_time_var.set(str(self.settings["delay_time"]))
            self.phone_number_var.set(self.settings["phone_number"])
            self.system_power_var.set("ON")

            messagebox.showinfo("Success", "System reset to default settings")
            self.app.update_status("System reset to defaults")

    def save_settings(self):
        """Save current settings."""
        try:
            delay_time = int(self.delay_time_var.get())
            if delay_time < 0:
                raise ValueError("Delay time must be positive")

            self.settings["system_name"] = self.system_name_var.get()
            self.settings["delay_time"] = delay_time
            self.settings["phone_number"] = self.phone_number_var.get()

            messagebox.showinfo("Success", "Settings saved successfully")
            self.app.update_status("Settings saved")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def cancel_changes(self):
        """Cancel changes and revert to saved settings."""
        self.system_name_var.set(self.settings["system_name"])
        self.delay_time_var.set(str(self.settings["delay_time"]))
        self.phone_number_var.set(self.settings["phone_number"])
        messagebox.showinfo("Info", "Changes cancelled")


class PasswordChangeDialog(tk.Toplevel):
    """Dialog for changing passwords."""

    def __init__(self, parent, password_type):
        """Initialize the password change dialog."""
        super().__init__(parent)
        self.result = None

        self.title(f"Change {password_type}")
        self.geometry("400x200")
        self.resizable(False, False)

        self.center_window()

        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Current Password:").pack(
            anchor=tk.W, pady=5
        )
        self.current_password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.current_password_entry.pack(pady=(0, 15))

        ttk.Label(main_frame, text="New Password:").pack(anchor=tk.W, pady=5)
        self.new_password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.new_password_entry.pack(pady=(0, 15))

        ttk.Label(main_frame, text="Confirm New Password:").pack(
            anchor=tk.W, pady=5
        )
        self.confirm_password_entry = ttk.Entry(main_frame, width=30, show="*")
        self.confirm_password_entry.pack(pady=(0, 20))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack()

        ok_btn = ttk.Button(
            button_frame, text="OK", command=self.ok_clicked, width=12
        )
        ok_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(
            button_frame, text="Cancel", command=self.cancel_clicked, width=12
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        self.current_password_entry.focus()

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def ok_clicked(self):
        """Handle OK button click and validate password."""
        current = self.current_password_entry.get()
        new = self.new_password_entry.get()
        confirm = self.confirm_password_entry.get()

        if not current or not new or not confirm:
            messagebox.showerror("Error", "All fields are required")
            return

        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return

        if len(new) < 4:
            messagebox.showerror(
                "Error", "Password must be at least 4 characters"
            )
            return

        self.result = new
        self.destroy()

    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.destroy()
