"""Sensor management panel for controlling and monitoring sensors."""

import tkinter as tk
from tkinter import messagebox, ttk

from .api_client import APIClient


class SensorPanel(tk.Toplevel):
    """Window for sensor management and testing."""

    def __init__(self, parent, user_id=None, log_refresh_callback=None):
        """Initialize the sensor panel window.

        Args:
            parent: Parent window
            user_id: Optional user ID for intrusion log updates
            log_refresh_callback: Optional callback to refresh intrusion log
        """
        super().__init__(parent)
        self.api_client = APIClient()
        self.user_id = user_id
        self.log_refresh_callback = log_refresh_callback

        self.title("Sensor Test")
        self.geometry("800x600")
        self.resizable(True, True)

        self.sensors = {}
        self.motion_sensor_ids = []
        self.windoor_sensor_ids = []

        self.setup_ui()
        self.load_sensors()

    def setup_ui(self):
        """Set up the user interface."""
        # Top frame with sensor controls
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # WinDoor Sensor section (left)
        windoor_frame = ttk.LabelFrame(top_frame, text="WinDoor Sensor", padding=10)
        windoor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(windoor_frame, text="ID range:").pack(anchor=tk.W, pady=2)
        self.windoor_range_label = ttk.Label(windoor_frame, text="1-4")
        self.windoor_range_label.pack(anchor=tk.W, pady=2)

        ttk.Label(windoor_frame, text="input ID:").pack(anchor=tk.W, pady=2)
        self.windoor_id_var = tk.StringVar(value="1")
        windoor_id_entry = ttk.Entry(
            windoor_frame, textvariable=self.windoor_id_var, width=10
        )
        windoor_id_entry.pack(anchor=tk.W, pady=2)

        ttk.Label(windoor_frame, text="Sensor Control:").pack(anchor=tk.W, pady=(10, 2))
        windoor_control_frame = ttk.Frame(windoor_frame)
        windoor_control_frame.pack(fill=tk.X, pady=2)

        self.windoor_arm_btn = ttk.Button(
            windoor_control_frame,
            text="Arm",
            command=self.arm_windoor,
            width=12,
        )
        self.windoor_arm_btn.pack(side=tk.LEFT, padx=2)

        self.windoor_disarm_btn = ttk.Button(
            windoor_control_frame,
            text="Disarm",
            command=self.disarm_windoor,
            width=12,
        )
        self.windoor_disarm_btn.pack(side=tk.LEFT, padx=2)

        ttk.Label(windoor_frame, text="Door Control:").pack(anchor=tk.W, pady=(10, 2))
        windoor_door_frame = ttk.Frame(windoor_frame)
        windoor_door_frame.pack(fill=tk.X, pady=2)

        self.windoor_open_btn = ttk.Button(
            windoor_door_frame,
            text="Open",
            command=self.open_windoor,
            width=12,
        )
        self.windoor_open_btn.pack(side=tk.LEFT, padx=2)

        self.windoor_close_btn = ttk.Button(
            windoor_door_frame,
            text="Close",
            command=self.close_windoor,
            width=12,
        )
        self.windoor_close_btn.pack(side=tk.LEFT, padx=2)

        motion_frame = ttk.LabelFrame(top_frame, text="Motion Detector", padding=10)
        motion_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(motion_frame, text="ID range:").pack(anchor=tk.W, pady=2)
        self.motion_range_label = ttk.Label(motion_frame, text="1-3")
        self.motion_range_label.pack(anchor=tk.W, pady=2)

        ttk.Label(motion_frame, text="input ID:").pack(anchor=tk.W, pady=2)
        self.motion_id_var = tk.StringVar(value="1")
        motion_id_entry = ttk.Entry(
            motion_frame, textvariable=self.motion_id_var, width=10
        )
        motion_id_entry.pack(anchor=tk.W, pady=2)

        ttk.Label(motion_frame, text="Sensor Control:").pack(anchor=tk.W, pady=(10, 2))
        motion_control_frame = ttk.Frame(motion_frame)
        motion_control_frame.pack(fill=tk.X, pady=2)

        self.motion_arm_btn = ttk.Button(
            motion_control_frame,
            text="Arm",
            command=self.arm_motion,
            width=12,
        )
        self.motion_arm_btn.pack(side=tk.LEFT, padx=2)

        self.motion_disarm_btn = ttk.Button(
            motion_control_frame,
            text="Disarm",
            command=self.disarm_motion,
            width=12,
        )
        self.motion_disarm_btn.pack(side=tk.LEFT, padx=2)

        ttk.Label(motion_frame, text="Motion Control:").pack(anchor=tk.W, pady=(10, 2))
        motion_detect_frame = ttk.Frame(motion_frame)
        motion_detect_frame.pack(fill=tk.X, pady=2)

        self.motion_trigger_btn = ttk.Button(
            motion_detect_frame,
            text="Detect",
            command=self.trigger_motion,
            width=12,
        )
        self.motion_trigger_btn.pack(side=tk.LEFT, padx=2)

        self.motion_release_btn = ttk.Button(
            motion_detect_frame,
            text="Clear",
            command=self.release_motion,
            width=12,
        )
        self.motion_release_btn.pack(side=tk.LEFT, padx=2)

        status_frame = ttk.LabelFrame(self, text="Sensor Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Window/Door Sensors section
        windoor_header = ttk.Frame(status_frame)
        windoor_header.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(
            windoor_header, text="Window/Door Sensors:", font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)

        windoor_list_frame = ttk.Frame(status_frame)
        windoor_list_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        windoor_columns = ("sensor_id", "location", "armed", "status")
        self.windoor_tree = ttk.Treeview(
            windoor_list_frame,
            columns=windoor_columns,
            show="headings",
            height=4,
        )
        self.windoor_tree.heading("sensor_id", text="ID")
        self.windoor_tree.heading("location", text="Location")
        self.windoor_tree.heading("armed", text="Armed")
        self.windoor_tree.heading("status", text="Status")

        self.windoor_tree.column("sensor_id", width=50)
        self.windoor_tree.column("location", width=150)
        self.windoor_tree.column("armed", width=80)
        self.windoor_tree.column("status", width=100)

        windoor_scrollbar = ttk.Scrollbar(
            windoor_list_frame,
            orient=tk.VERTICAL,
            command=self.windoor_tree.yview,
        )
        self.windoor_tree.configure(yscrollcommand=windoor_scrollbar.set)

        self.windoor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        windoor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Motion Detectors section
        motion_header = ttk.Frame(status_frame)
        motion_header.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(
            motion_header, text="Motion Detectors:", font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)

        motion_list_frame = ttk.Frame(status_frame)
        motion_list_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        motion_columns = ("sensor_id", "location", "armed", "status")
        self.motion_tree = ttk.Treeview(
            motion_list_frame,
            columns=motion_columns,
            show="headings",
            height=4,
        )
        self.motion_tree.heading("sensor_id", text="ID")
        self.motion_tree.heading("location", text="Location")
        self.motion_tree.heading("armed", text="Armed")
        self.motion_tree.heading("status", text="Status")

        self.motion_tree.column("sensor_id", width=50)
        self.motion_tree.column("location", width=150)
        self.motion_tree.column("armed", width=80)
        self.motion_tree.column("status", width=100)

        motion_scrollbar = ttk.Scrollbar(
            motion_list_frame,
            orient=tk.VERTICAL,
            command=self.motion_tree.yview,
        )
        self.motion_tree.configure(yscrollcommand=motion_scrollbar.set)

        self.motion_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        motion_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_sensors(self):
        """Load sensors from API and update UI."""
        try:
            response = self.api_client.list_sensors()
            sensors_list = response.get("sensors", [])

            self.sensors = {}
            self.motion_sensor_ids = []
            self.windoor_sensor_ids = []

            for sensor in sensors_list:
                sensor_id = sensor["sensor_id"]
                sensor_type = sensor["sensor_type"]
                self.sensors[(sensor_type, sensor_id)] = sensor

                if sensor_type == "motion":
                    if sensor_id not in self.motion_sensor_ids:
                        self.motion_sensor_ids.append(sensor_id)
                elif sensor_type == "windoor":
                    if sensor_id not in self.windoor_sensor_ids:
                        self.windoor_sensor_ids.append(sensor_id)

            if self.motion_sensor_ids:
                min_id = min(self.motion_sensor_ids)
                max_id = max(self.motion_sensor_ids)
                self.motion_range_label.config(text=f"{min_id}-{max_id}")

            if self.windoor_sensor_ids:
                min_id = min(self.windoor_sensor_ids)
                max_id = max(self.windoor_sensor_ids)
                self.windoor_range_label.config(text=f"{min_id}-{max_id}")

            self.refresh_status()
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
                    "Error", f"Failed to load sensors: {error_message}"
                )

    def refresh_status(self):
        """Refresh sensor status display."""
        # Clear existing items
        for item in self.windoor_tree.get_children():
            self.windoor_tree.delete(item)
        for item in self.motion_tree.get_children():
            self.motion_tree.delete(item)

        # Update windoor sensors
        windoor_sensors = [
            (sid, self.sensors.get(("windoor", sid)))
            for sid in sorted(self.windoor_sensor_ids)
        ]
        for sensor_id, sensor in windoor_sensors:
            if sensor:
                is_armed = sensor.get("is_armed", False)
                # For windoor sensors, is_triggered represents is_opened
                is_opened = sensor.get("is_triggered", False)
                location = sensor.get("location", "Unknown")

                armed_status = "Armed" if is_armed else "Disarmed"
                door_status = "OPEN" if is_opened else "CLOSED"

                self.windoor_tree.insert(
                    "",
                    tk.END,
                    values=(sensor_id, location, armed_status, door_status),
                )

        # Update motion sensors
        motion_sensors = [
            (sid, self.sensors.get(("motion", sid)))
            for sid in sorted(self.motion_sensor_ids)
        ]
        for sensor_id, sensor in motion_sensors:
            if sensor:
                is_armed = sensor.get("is_armed", False)
                is_triggered = sensor.get("is_triggered", False)
                location = sensor.get("location", "Unknown")

                armed_status = "Armed" if is_armed else "Disarmed"
                motion_status = "DETECTED" if is_triggered else "CLEAR"

                self.motion_tree.insert(
                    "",
                    tk.END,
                    values=(sensor_id, location, armed_status, motion_status),
                )

        # Force UI update to ensure status is displayed
        self.update_idletasks()

    def get_windoor_id(self):
        """Get windoor sensor ID from input."""
        try:
            sensor_id = int(self.windoor_id_var.get())
            if sensor_id not in self.windoor_sensor_ids:
                min_id = min(self.windoor_sensor_ids)
                max_id = max(self.windoor_sensor_ids)
                messagebox.showerror(
                    "Error", f"Invalid sensor ID. Valid range: {min_id}-{max_id}"
                )
                return None
            return sensor_id
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid sensor ID")
            return None

    def get_motion_id(self):
        """Get motion sensor ID from input."""
        try:
            sensor_id = int(self.motion_id_var.get())
            if sensor_id not in self.motion_sensor_ids:
                min_id = min(self.motion_sensor_ids)
                max_id = max(self.motion_sensor_ids)
                messagebox.showerror(
                    "Error", f"Invalid sensor ID. Valid range: {min_id}-{max_id}"
                )
                return None
            return sensor_id
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid sensor ID")
            return None

    def arm_windoor(self):
        """Arm a windoor sensor."""
        sensor_id = self.get_windoor_id()
        if sensor_id is None:
            return

        # Check if the sensor is currently open before arming
        try:
            sensor_status = self.api_client.get_sensor_status("windoor", sensor_id)
            is_opened = sensor_status.get("is_opened", False)

            if is_opened:
                messagebox.showerror("Error", "doors and windows not closed")
                return
        except Exception:
            # If we can't get sensor status, continue with arming attempt
            # The API will handle the validation
            pass

        try:
            self.api_client.arm_windoor_sensor(sensor_id)
            messagebox.showinfo("Success", f"Windoor sensor {sensor_id} armed")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            elif "doors and windows not closed" in error_message.lower():
                messagebox.showerror("Error", "doors and windows not closed")
            else:
                messagebox.showerror("Error", f"Failed to arm sensor: {error_message}")

    def disarm_windoor(self):
        """Disarm a windoor sensor."""
        sensor_id = self.get_windoor_id()
        if sensor_id is None:
            return

        try:
            self.api_client.disarm_windoor_sensor(sensor_id)
            messagebox.showinfo("Success", f"Windoor sensor {sensor_id} disarmed")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror(
                    "Error", f"Failed to disarm sensor: {error_message}"
                )

    def open_windoor(self):
        """Open a windoor sensor."""
        sensor_id = self.get_windoor_id()
        if sensor_id is None:
            return

        try:
            self.api_client.open_windoor_sensor(sensor_id)
            messagebox.showinfo("Success", f"Windoor sensor {sensor_id} opened")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror("Error", f"Failed to open sensor: {error_message}")

    def close_windoor(self):
        """Close a windoor sensor."""
        sensor_id = self.get_windoor_id()
        if sensor_id is None:
            return

        try:
            self.api_client.close_windoor_sensor(sensor_id)
            messagebox.showinfo("Success", f"Windoor sensor {sensor_id} closed")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror(
                    "Error", f"Failed to close sensor: {error_message}"
                )

    def arm_motion(self):
        """Arm a motion sensor."""
        sensor_id = self.get_motion_id()
        if sensor_id is None:
            return

        try:
            self.api_client.arm_motion_sensor(sensor_id)
            messagebox.showinfo("Success", f"Motion sensor {sensor_id} armed")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror("Error", f"Failed to arm sensor: {error_message}")

    def disarm_motion(self):
        """Disarm a motion sensor."""
        sensor_id = self.get_motion_id()
        if sensor_id is None:
            return

        try:
            self.api_client.disarm_motion_sensor(sensor_id)
            messagebox.showinfo("Success", f"Motion sensor {sensor_id} disarmed")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror(
                    "Error", f"Failed to disarm sensor: {error_message}"
                )

    def trigger_motion(self):
        """Trigger a motion sensor."""
        sensor_id = self.get_motion_id()
        if sensor_id is None:
            return

        try:
            self.api_client.trigger_motion_sensor(sensor_id)
            messagebox.showinfo("Success", f"Motion sensor {sensor_id} triggered")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror(
                    "Error", f"Failed to trigger sensor: {error_message}"
                )

    def release_motion(self):
        """Release a motion sensor."""
        sensor_id = self.get_motion_id()
        if sensor_id is None:
            return

        try:
            self.api_client.release_motion_sensor(sensor_id)
            messagebox.showinfo("Success", f"Motion sensor {sensor_id} released")
            self.load_sensors()
            # Refresh intrusion log after action
            if self.log_refresh_callback:
                try:
                    self.log_refresh_callback()
                except Exception:
                    pass  # Silently fail if log refresh fails
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror(
                    "Error", f"Failed to release sensor: {error_message}"
                )
