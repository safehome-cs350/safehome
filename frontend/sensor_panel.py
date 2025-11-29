"""Sensor management panel for controlling and monitoring sensors."""

import tkinter as tk
from tkinter import messagebox, ttk

from .api_client import APIClient


class SensorPanel(tk.Toplevel):
    """Window for sensor management and testing."""

    def __init__(self, parent):
        """Initialize the sensor panel window."""
        super().__init__(parent)
        self.api_client = APIClient()

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

        ttk.Label(
            status_frame, text="Window/Door Sensors:", font=("Arial", 10, "bold")
        ).pack(anchor=tk.W, pady=(0, 5))
        self.windoor_status_text = tk.Text(
            status_frame, height=4, width=80, wrap=tk.WORD, bg="#2b2b2b", fg="#ffffff"
        )
        self.windoor_status_text.pack(fill=tk.X, pady=2)

        ttk.Label(
            status_frame, text="Motion Detectors:", font=("Arial", 10, "bold")
        ).pack(anchor=tk.W, pady=(10, 5))
        self.motion_status_text = tk.Text(
            status_frame, height=4, width=80, wrap=tk.WORD, bg="#2b2b2b", fg="#ffffff"
        )
        self.motion_status_text.pack(fill=tk.X, pady=2)

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
        self.windoor_status_text.config(state=tk.NORMAL)
        self.motion_status_text.config(state=tk.NORMAL)
        self.windoor_status_text.delete(1.0, tk.END)
        self.motion_status_text.delete(1.0, tk.END)

        windoor_sensors = [
            (sid, self.sensors.get(("windoor", sid)))
            for sid in sorted(self.windoor_sensor_ids)
        ]
        for sensor_id, sensor in windoor_sensors:
            if sensor:
                is_armed = sensor.get("is_armed", False)
                is_opened = sensor.get("is_triggered", False)
                sensor_status = "ON" if is_armed else "OFF"
                door_status = "OPEN" if is_opened else "CLOSED"

                armed_indicator = "●" if is_armed else "○"
                opened_indicator = "●" if is_opened else "○"
                status_line = (
                    f"ID {sensor_id}: Sensor[{armed_indicator} {sensor_status}] "
                    f"Door[{opened_indicator} {door_status}]\n"
                )
                self.windoor_status_text.insert(tk.END, status_line)

        motion_sensors = [
            (sid, self.sensors.get(("motion", sid)))
            for sid in sorted(self.motion_sensor_ids)
        ]
        for sensor_id, sensor in motion_sensors:
            if sensor:
                is_armed = sensor.get("is_armed", False)
                is_triggered = sensor.get("is_triggered", False)
                sensor_status = "ON" if is_armed else "OFF"
                motion_status = "DETECTED" if is_triggered else "CLEAR"

                armed_indicator = "●" if is_armed else "○"
                triggered_indicator = "●" if is_triggered else "○"
                status_line = (
                    f"ID {sensor_id}: Sensor[{armed_indicator} {sensor_status}] "
                    f"Motion[{triggered_indicator} {motion_status}]\n"
                )
                self.motion_status_text.insert(tk.END, status_line)

        self.windoor_status_text.config(state=tk.DISABLED)
        self.motion_status_text.config(state=tk.DISABLED)

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

        try:
            self.api_client.arm_windoor_sensor(sensor_id)
            messagebox.showinfo("Success", f"Windoor sensor {sensor_id} armed")
            self.load_sensors()
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
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
        except Exception as e:
            error_message = str(e)
            if "404" in error_message:
                messagebox.showerror("Error", "Sensor not found")
            else:
                messagebox.showerror(
                    "Error", f"Failed to release sensor: {error_message}"
                )
