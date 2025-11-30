"""Security panel for system security management."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from .api_client import APIClient
from .safety_zone_dialog import SafetyZoneDialog


class SecurityPanel(ttk.Frame):
    """Panel for security system management."""

    def __init__(self, parent, app):
        """Initialize the security panel."""
        super().__init__(parent)
        self.app = app
        self.api_client = APIClient()

        self.system_armed = False
        self.current_mode = None
        self.safety_zones = {}  # name -> zone data
        self.available_devices = []  # List of device dicts with id and type
        self.intrusion_log = []
        self._loading_mode = False  # Flag to prevent saving during load

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Set up the user interface."""
        left_frame = ttk.LabelFrame(self, text="System Control", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        mode_frame = ttk.LabelFrame(left_frame, text="System Modes", padding=10)
        mode_frame.pack(fill=tk.X, pady=10)

        self.mode_var = tk.StringVar(value="away")
        self.mode_var.trace_add("write", self.on_mode_change)
        modes = [
            ("Away", "away"),
            ("Stay", "home"),
            ("Extend Travel", "extended_travel"),
            ("Overnight Travel", "overnight_travel"),
        ]

        for text, value in modes:
            radio = ttk.Radiobutton(
                mode_frame, text=text, variable=self.mode_var, value=value
            )
            radio.pack(anchor=tk.W, pady=2)

        panic_frame = ttk.Frame(left_frame)
        panic_frame.pack(fill=tk.X, pady=10)

        panic_btn = ttk.Button(
            panic_frame,
            text="🚨 PANIC ALARM",
            command=self.trigger_panic,
            width=20,
            style="Panic.TButton",
        )
        panic_btn.pack(pady=5)

        monitoring_btn = ttk.Button(
            panic_frame,
            text="Call Monitoring Service",
            command=self.call_monitoring_service,
            width=20,
        )
        monitoring_btn.pack(pady=5)

        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        zones_frame = ttk.LabelFrame(right_frame, text="Safety Zones", padding=10)
        zones_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        zones_list_frame = ttk.Frame(zones_frame)
        zones_list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "status", "devices")
        self.zones_tree = ttk.Treeview(
            zones_list_frame, columns=columns, show="headings", height=8
        )
        self.zones_tree.heading("name", text="Name")
        self.zones_tree.heading("status", text="Status")
        self.zones_tree.heading("devices", text="Devices")

        self.zones_tree.column("name", width=150)
        self.zones_tree.column("status", width=100)
        self.zones_tree.column("devices", width=200)

        scrollbar_zones = ttk.Scrollbar(
            zones_list_frame, orient=tk.VERTICAL, command=self.zones_tree.yview
        )
        self.zones_tree.configure(yscrollcommand=scrollbar_zones.set)

        self.zones_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_zones.pack(side=tk.RIGHT, fill=tk.Y)

        zone_btn_frame = ttk.Frame(zones_frame)
        zone_btn_frame.pack(fill=tk.X, pady=5)

        create_btn = ttk.Button(
            zone_btn_frame,
            text="Create Zone",
            command=self.create_zone,
            width=12,
        )
        create_btn.pack(side=tk.LEFT, padx=2)
        edit_btn = ttk.Button(
            zone_btn_frame, text="Edit Zone", command=self.edit_zone, width=12
        )
        edit_btn.pack(side=tk.LEFT, padx=2)
        delete_btn = ttk.Button(
            zone_btn_frame,
            text="Delete Zone",
            command=self.delete_zone,
            width=12,
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(
            zone_btn_frame,
            text="Arm/Disarm Zone",
            command=self.toggle_zone,
            width=15,
        ).pack(side=tk.LEFT, padx=2)

        log_frame = ttk.LabelFrame(right_frame, text="Intrusion Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        log_list_frame = ttk.Frame(log_frame)
        log_list_frame.pack(fill=tk.BOTH, expand=True)

        log_columns = ("timestamp", "alarm_type", "location", "description")
        self.log_tree = ttk.Treeview(
            log_list_frame, columns=log_columns, show="headings", height=8
        )
        self.log_tree.heading("timestamp", text="Timestamp")
        self.log_tree.heading("alarm_type", text="Alarm Type")
        self.log_tree.heading("location", text="Location")
        self.log_tree.heading("description", text="Description")

        self.log_tree.column("timestamp", width=150)
        self.log_tree.column("alarm_type", width=120)
        self.log_tree.column("location", width=100)
        self.log_tree.column("description", width=200)

        scrollbar_log = ttk.Scrollbar(
            log_list_frame, orient=tk.VERTICAL, command=self.log_tree.yview
        )
        self.log_tree.configure(yscrollcommand=scrollbar_log.set)

        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)

    def load_safety_zones(self):
        """Load safety zones from GET API and refresh display."""
        if not self.app.current_user:
            return

        try:
            response = self.api_client.get_safety_zones(self.app.current_user)
            zones_list = response.get("safety_zones", [])
            self.safety_zones = {}
            for zone in zones_list:
                # Extract device IDs from devices list
                devices = zone.get("devices", [])
                device_ids = [
                    device.get("id") for device in devices if device.get("id")
                ]
                self.safety_zones[zone["name"]] = {
                    "name": zone["name"],
                    "device_ids": device_ids,
                    "is_armed": zone.get("is_armed", False),
                }
            self.refresh_zones_display()
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to load safety zones: {error_message}"
                )

    def load_data(self):
        """Load safety zones, devices, and intrusion log from API."""
        if not self.app.current_user:
            return

        try:
            # Load safety zones using GET API
            self.load_safety_zones()

            # Load available devices and zones configuration
            config_response = self.api_client.configure_safety_zone_interface(
                self.app.current_user
            )
            self.available_devices = config_response.get("available_devices", [])

            # Load SafeHome modes
            modes_response = self.api_client.get_safehome_modes(self.app.current_user)
            self.current_mode = modes_response.get("current_mode", "away")
            # Set flag to prevent saving during load
            self._loading_mode = True
            self.mode_var.set(self.current_mode)
            self._loading_mode = False

            # Load intrusion log
            self.load_intrusion_log()
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                messagebox.showerror(
                    "Error",
                    "Cannot connect to backend server. "
                    "Please ensure the backend is running.",
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to load security data: {error_message}"
                )

    def load_intrusion_log(self):
        """Load intrusion log from API."""
        if not self.app.current_user:
            return

        try:
            response = self.api_client.view_intrusion_log(self.app.current_user)
            events = response.get("events", [])
            self.intrusion_log = []
            for event in events:
                timestamp_str = event.get("timestamp", "")
                # Parse ISO format timestamp
                try:
                    if "T" in timestamp_str:
                        dt = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                    else:
                        dt = datetime.fromisoformat(timestamp_str)
                    timestamp_display = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    timestamp_display = timestamp_str

                self.intrusion_log.append(
                    (
                        timestamp_display,
                        event.get("alarm_type", "").upper(),
                        event.get("location", ""),
                        event.get("description", ""),
                    )
                )
            self.refresh_log_display()
        except Exception as e:
            error_message = str(e)
            if "Connection" in error_message or "refused" in error_message.lower():
                pass  # Already shown in load_data
            else:
                # Silently fail for log loading
                pass

    def arm_system(self):
        """Arm the security system."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        result = messagebox.askyesno(
            "Arm System", "Are you sure you want to arm the system?"
        )
        if result:
            try:
                mode_type = self.mode_var.get()
                # Set the SafeHome mode (this also arms the system)
                response = self.api_client.set_safehome_mode(
                    self.app.current_user, mode_type
                )
                self.system_armed = True
                self.current_mode = response.get("current_mode", mode_type)
                self.app.update_status(
                    f"System Armed - Mode: {self.current_mode.title()}"
                )
                messagebox.showinfo("Success", "System armed successfully")
                self.load_data()  # Reload to get updated state
            except Exception as e:
                error_message = str(e)
                if "doors and windows not closed" in error_message:
                    messagebox.showerror(
                        "Error",
                        "Cannot arm system: doors and windows not closed",
                    )
                elif (
                    "Connection" in error_message or "refused" in error_message.lower()
                ):
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        f"Failed to arm system: {error_message}",
                    )

    def disarm_system(self):
        """Disarm the security system."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        result = messagebox.askyesno(
            "Disarm System", "Are you sure you want to disarm the system?"
        )
        if result:
            try:
                self.api_client.disarm(self.app.current_user)
                self.system_armed = False
                self.app.update_status("System Disarmed")
                messagebox.showinfo("Success", "System disarmed successfully")
                self.load_data()  # Reload to get updated state
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to disarm system: {error_message}"
                    )

    def trigger_panic(self):
        """Trigger panic alarm."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        result = messagebox.askyesno(
            "Panic Alarm",
            "This will trigger a panic alarm and call monitoring service. Continue?",
        )
        if result:
            try:
                self.api_client.panic_call(
                    self.app.current_user, location="Control Panel"
                )
                messagebox.showwarning(
                    "Panic Alarm",
                    "Panic alarm activated! Monitoring service notified.",
                )
                self.app.update_status("Panic alarm activated")
                self.load_intrusion_log()  # Reload log to show panic event
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to trigger panic: {error_message}"
                    )

    def call_monitoring_service(self):
        """Call the monitoring service (same as panic)."""
        self.trigger_panic()

    def create_zone(self):
        """Create a new safety zone."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        # Ensure available devices are loaded
        if not self.available_devices:
            try:
                config_response = self.api_client.configure_safety_zone_interface(
                    self.app.current_user
                )
                self.available_devices = config_response.get("available_devices", [])
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to load devices: {error_message}"
                    )
                return

        dialog = SafetyZoneDialog(self, None, self.available_devices)
        self.wait_window(dialog)  # Wait for dialog to close
        if dialog.result:
            try:
                self.api_client.create_safety_zone(
                    self.app.current_user,
                    dialog.result["name"],
                    dialog.result["device_ids"],
                )
                messagebox.showinfo(
                    "Success",
                    f"Zone '{dialog.result['name']}' created successfully",
                )
                # Reload zones from GET API after creation
                self.load_data()
                self.app.update_status(f"Zone '{dialog.result['name']}' created")
            except Exception as e:
                error_message = str(e)
                if "Same safety zone exists" in error_message:
                    messagebox.showerror(
                        "Error", "A zone with this name already exists"
                    )
                elif (
                    "Connection" in error_message or "refused" in error_message.lower()
                ):
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to create zone: {error_message}"
                    )

    def edit_zone(self):
        """Edit an existing safety zone."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        selected = self.zones_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a zone to edit")
            return

        item = self.zones_tree.item(selected[0])
        original_zone_name = item["values"][0]  # Store original name

        if original_zone_name in self.safety_zones:
            zone_data = self.safety_zones[original_zone_name].copy()
            # Ensure available devices are loaded
            if not self.available_devices:
                try:
                    config_response = self.api_client.configure_safety_zone_interface(
                        self.app.current_user
                    )
                    self.available_devices = config_response.get(
                        "available_devices", []
                    )
                except Exception as e:
                    error_message = str(e)
                    if (
                        "Connection" in error_message
                        or "refused" in error_message.lower()
                    ):
                        messagebox.showerror(
                            "Error",
                            "Cannot connect to backend server. "
                            "Please ensure the backend is running.",
                        )
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to load devices: {error_message}"
                        )
                    return

            dialog = SafetyZoneDialog(self, zone_data, self.available_devices)
            self.wait_window(dialog)  # Wait for dialog to close
            if dialog.result:
                try:
                    new_name = dialog.result["name"]
                    new_device_ids = dialog.result["device_ids"]

                    # If name changed, we need to delete old zone and create new one
                    # because backend update_safety_zone only updates devices, not name
                    if original_zone_name != new_name:
                        # Check if new name already exists
                        if new_name in self.safety_zones:
                            messagebox.showerror(
                                "Error", "A zone with this name already exists"
                            )
                            return

                        # Delete old zone and create new one
                        self.api_client.delete_safety_zone(
                            self.app.current_user, original_zone_name
                        )
                        self.api_client.create_safety_zone(
                            self.app.current_user, new_name, new_device_ids
                        )
                        messagebox.showinfo(
                            "Success",
                            f"Zone '{original_zone_name}' renamed to "
                            f"'{new_name}' and updated",
                        )
                    else:
                        # Only devices changed, use update endpoint with original name
                        self.api_client.update_safety_zone(
                            self.app.current_user, original_zone_name, new_device_ids
                        )
                        messagebox.showinfo(
                            "Success",
                            f"Zone '{new_name}' updated successfully",
                        )

                    # Reload zones from GET API after update
                    self.load_data()
                    self.app.update_status(f"Zone '{new_name}' updated")
                except Exception as e:
                    error_message = str(e)
                    if (
                        "Connection" in error_message
                        or "refused" in error_message.lower()
                    ):
                        messagebox.showerror(
                            "Error",
                            "Cannot connect to backend server. "
                            "Please ensure the backend is running.",
                        )
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to update zone: {error_message}"
                        )

    def delete_zone(self):
        """Delete a safety zone."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        selected = self.zones_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a zone to delete")
            return

        item = self.zones_tree.item(selected[0])
        zone_name = item["values"][0]

        result = messagebox.askyesno(
            "Delete Zone",
            f"Are you sure you want to delete zone '{zone_name}'?",
        )
        if result:
            try:
                self.api_client.delete_safety_zone(self.app.current_user, zone_name)
                messagebox.showinfo(
                    "Success", f"Zone '{zone_name}' deleted successfully"
                )
                # Reload zones from GET API after deletion
                self.load_data()
                self.app.update_status(f"Zone '{zone_name}' deleted")
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to delete zone: {error_message}"
                    )

    def toggle_zone(self):
        """Toggle zone armed/disarmed status."""
        if not self.app.current_user:
            messagebox.showerror("Error", "No user logged in")
            return

        selected = self.zones_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a zone to arm/disarm")
            return

        item = self.zones_tree.item(selected[0])
        zone_name = item["values"][0]

        if zone_name in self.safety_zones:
            zone = self.safety_zones[zone_name]
            is_armed = zone.get("is_armed", False)
            try:
                if is_armed:
                    self.api_client.disarm_safety_zone(self.app.current_user, zone_name)
                    action = "Disarmed"
                else:
                    self.api_client.arm_safety_zone(self.app.current_user, zone_name)
                    action = "Armed"
                messagebox.showinfo("Success", f"Zone '{zone_name}' {action.lower()}")
                # Reload zones from GET API after toggle
                self.load_safety_zones()
                # Refresh intrusion log after zone action
                self.load_intrusion_log()
                self.app.update_status(f"Zone '{zone_name}' {action.lower()}")
            except Exception as e:
                error_message = str(e)
                if "Connection" in error_message or "refused" in error_message.lower():
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to toggle zone: {error_message}"
                    )

    def refresh_zones_display(self):
        """Refresh the zones display."""
        for item in self.zones_tree.get_children():
            self.zones_tree.delete(item)

        for zone_name, zone in sorted(self.safety_zones.items()):
            status = "Armed" if zone.get("is_armed", False) else "Disarmed"
            device_ids = zone.get("device_ids", [])
            # Create device display string
            device_str = ", ".join([f"Device {did}" for did in device_ids])
            if not device_str:
                device_str = "No devices"
            self.zones_tree.insert(
                "",
                tk.END,
                values=(zone_name, status, device_str),
            )

    def refresh_log_display(self):
        """Refresh the log display."""
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        for entry in self.intrusion_log:
            self.log_tree.insert("", tk.END, values=entry)

    def on_mode_change(self, *args):
        """Handle mode change event - save mode to backend."""
        if not self.app.current_user:
            return

        # Skip if this is during initialization
        if self._loading_mode or self.current_mode is None:
            return

        new_mode = self.mode_var.get()
        # Only save if mode actually changed
        if new_mode != self.current_mode:
            try:
                response = self.api_client.set_safehome_mode(
                    self.app.current_user, new_mode
                )
                self.current_mode = response.get("current_mode", new_mode)
                self.system_armed = response.get("is_system_armed", False)
                self.app.update_status(f"Mode changed to {self.current_mode.title()}")
                # Reload data to ensure consistency
                self.load_data()
            except Exception as e:
                error_message = str(e)
                # Revert to previous mode on error
                self.mode_var.set(self.current_mode)
                if "doors and windows not closed" in error_message:
                    messagebox.showerror(
                        "Error",
                        "Cannot set mode: doors and windows not closed",
                    )
                elif (
                    "Connection" in error_message or "refused" in error_message.lower()
                ):
                    messagebox.showerror(
                        "Error",
                        "Cannot connect to backend server. "
                        "Please ensure the backend is running.",
                    )
                else:
                    messagebox.showerror(
                        "Error", f"Failed to set mode: {error_message}"
                    )
