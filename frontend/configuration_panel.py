"""Configuration panel for system settings."""

import tkinter as tk
from tkinter import messagebox, ttk

from .api_client import APIClient


class ConfigurationPanel(ttk.Frame):
    """Panel for system configuration and settings."""

    def __init__(self, parent, app):
        """Initialize the configuration panel."""
        super().__init__(parent)
        self.app = app
        self.api_client = APIClient()

        self.settings = {
            "password1": "12345678",
            "password2": "abcdefgh",
            "master_password": "1234",
            "guest_password": "5678",
            "delay_time": 300,
            "phone_number": "01012345678",
        }

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Set up the user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        settings_frame = ttk.LabelFrame(main_frame, text="System Settings", padding=15)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        row = 0
        ttk.Label(settings_frame, text="Password 1:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.password1_var = tk.StringVar(value="")
        ttk.Entry(
            settings_frame,
            textvariable=self.password1_var,
            width=30,
            show="*",
        ).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        row += 1
        ttk.Label(settings_frame, text="Password 2:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.password2_var = tk.StringVar(value="")
        ttk.Entry(
            settings_frame,
            textvariable=self.password2_var,
            width=30,
            show="*",
        ).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        row += 1
        ttk.Label(settings_frame, text="Master Password:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.master_password_var = tk.StringVar(value="")
        ttk.Entry(
            settings_frame,
            textvariable=self.master_password_var,
            width=30,
            show="*",
        ).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        row += 1
        ttk.Label(settings_frame, text="Guest Password:").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.guest_password_var = tk.StringVar(value="")
        ttk.Entry(
            settings_frame,
            textvariable=self.guest_password_var,
            width=30,
            show="*",
        ).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        row += 1
        ttk.Label(settings_frame, text="Delay Time (seconds):").grid(
            row=row, column=0, sticky=tk.W, pady=5, padx=5
        )
        self.delay_time_var = tk.StringVar(value=str(self.settings["delay_time"]))
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
        self.phone_number_var = tk.StringVar(value=self.settings["phone_number"])
        ttk.Entry(settings_frame, textvariable=self.phone_number_var, width=30).grid(
            row=row, column=1, pady=5, padx=5, sticky=tk.W
        )

        control_frame = ttk.LabelFrame(main_frame, text="System Control", padding=15)
        control_frame.pack(fill=tk.X, pady=10)

        system_control_frame = ttk.Frame(control_frame)
        system_control_frame.pack(fill=tk.X, pady=5)

        ttk.Label(system_control_frame, text="System Power:").pack(side=tk.LEFT, padx=5)
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
            text="Save Changes",
            command=self.save_settings,
            width=20,
        )
        save_btn.pack(side=tk.LEFT, padx=5)

    def load_config(self):
        """Load current user's configuration from the backend."""
        try:
            config = self.api_client.get_config(self.app.current_user)
            password1 = config.get("password1", "")
            password2 = config.get("password2", "")
            master_password = config.get("master_password", "")
            guest_password = config.get("guest_password", "")

            self.password1_var.set("********" if password1 else "")
            self.password2_var.set("********" if password2 else "")
            self.master_password_var.set("********" if master_password else "")
            self.guest_password_var.set("********" if guest_password else "")
            self.delay_time_var.set(str(config.get("delay_time", 300)))
            phone_number = config.get("phone_number", "")
            self.phone_number_var.set(phone_number if phone_number else "")

            self.settings["delay_time"] = config.get("delay_time", 300)
            self.settings["phone_number"] = phone_number if phone_number else ""
        except Exception:
            # Fields will remain with default/empty values
            pass

    def turn_system_on(self):
        """Turn the system on."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        result = messagebox.askyesno(
            "Turn System On", "Are you sure you want to turn the system on?"
        )
        if result:
            try:
                self.api_client.power_on(self.app.current_user)
                self.system_power_var.set("ON")
                messagebox.showinfo("Success", "System turned on")
                self.app.update_status("System turned on")
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    error_message = (
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running."
                    )
                messagebox.showerror(
                    "Error", f"Failed to turn system on: {error_message}"
                )

    def turn_system_off(self):
        """Turn the system off."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        result = messagebox.askyesno(
            "Turn System Off", "Are you sure you want to turn the system off?"
        )
        if result:
            try:
                self.api_client.power_off(self.app.current_user)
                self.system_power_var.set("OFF")
                messagebox.showinfo("Success", "System turned off")
                self.app.update_status("System turned off")
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    error_message = (
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running."
                    )
                messagebox.showerror(
                    "Error", f"Failed to turn system off: {error_message}"
                )

    def reset_system(self):
        """Reset system to default settings."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        result = messagebox.askyesno(
            "Reset System",
            "This will reset all system settings to defaults. Are you sure?",
        )
        if result:
            try:
                default_values = {
                    "password1": "12345678",
                    "password2": "abcdefgh",
                    "master_password": "1234",
                    "guest_password": "5678",
                    "delay_time": 300,
                    "phone_number": "01012345678",
                }

                self.api_client.config(
                    user_id=self.app.current_user,
                    password1=default_values["password1"],
                    password2=default_values["password2"],
                    master_password=default_values["master_password"],
                    guest_password=default_values["guest_password"],
                    delay_time=default_values["delay_time"],
                    phone_number=default_values["phone_number"],
                )

                self.settings = default_values.copy()
                self.load_config()

                messagebox.showinfo("Success", "System reset to default settings")
                self.app.update_status("System reset to defaults")
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    error_message = (
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running."
                    )
                messagebox.showerror(
                    "Error", f"Failed to reset system: {error_message}"
                )

    def save_settings(self):
        """Save current settings."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        try:
            delay_time = int(self.delay_time_var.get())
            if delay_time < 300:
                raise ValueError("Delay time must be at least 300 seconds")

            phone_number = self.phone_number_var.get().strip()
            password1 = self.password1_var.get().strip()
            password2 = self.password2_var.get().strip()
            master_password = self.master_password_var.get().strip()
            guest_password = self.guest_password_var.get().strip()

            config_params = {
                "user_id": self.app.current_user,
                "delay_time": delay_time,
            }

            if phone_number:
                config_params["phone_number"] = phone_number

            # Only include passwords if they've been changed
            if password1 and password1 != "********":
                config_params["password1"] = password1
            if password2 and password2 != "********":
                config_params["password2"] = password2
            if master_password and master_password != "********":
                config_params["master_password"] = master_password
            if guest_password and guest_password != "********":
                config_params["guest_password"] = guest_password

            self.api_client.config(**config_params)
            self.load_config()

            messagebox.showinfo("Success", "Settings saved successfully")
            self.app.update_status("Settings saved")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            error_message = str(e)
            if "400" in error_message and "300" in error_message:
                messagebox.showerror("Error", "Delay time must be at least 300 seconds")
            elif "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to save settings: {error_message}"
                )
