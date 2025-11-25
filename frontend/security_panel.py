import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from .safety_zone_dialog import SafetyZoneDialog


class SecurityPanel(ttk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.system_armed = False
        self.system_mode = "disarmed"
        self.safety_zones = {}
        self.intrusion_log = []

        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.LabelFrame(self, text="System Control", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill=tk.X, pady=5)

        ttk.Label(status_frame, text="System Status:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="DISARMED", font=("Arial", 12, "bold"), foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=10)

        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.arm_btn = ttk.Button(control_frame, text="Arm System", command=self.arm_system, width=20)
        self.arm_btn.pack(pady=5)

        self.disarm_btn = ttk.Button(
            control_frame,
            text="Disarm System",
            command=self.disarm_system,
            width=20,
            state=tk.DISABLED,
        )
        self.disarm_btn.pack(pady=5)

        mode_frame = ttk.LabelFrame(left_frame, text="System Modes", padding=10)
        mode_frame.pack(fill=tk.X, pady=10)

        self.mode_var = tk.StringVar(value="away")
        modes = [
            ("Away", "away"),
            ("Stay", "stay"),
            ("Extend Travel", "extend_travel"),
            ("Overnight Travel", "overnight_travel"),
        ]

        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=value).pack(anchor=tk.W, pady=2)

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

        columns = ("zone_id", "name", "status", "sensors")
        self.zones_tree = ttk.Treeview(zones_list_frame, columns=columns, show="headings", height=8)
        self.zones_tree.heading("zone_id", text="Zone ID")
        self.zones_tree.heading("name", text="Name")
        self.zones_tree.heading("status", text="Status")
        self.zones_tree.heading("sensors", text="Sensors")

        self.zones_tree.column("zone_id", width=80)
        self.zones_tree.column("name", width=150)
        self.zones_tree.column("status", width=100)
        self.zones_tree.column("sensors", width=100)

        scrollbar_zones = ttk.Scrollbar(zones_list_frame, orient=tk.VERTICAL, command=self.zones_tree.yview)
        self.zones_tree.configure(yscrollcommand=scrollbar_zones.set)

        self.zones_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_zones.pack(side=tk.RIGHT, fill=tk.Y)

        zone_btn_frame = ttk.Frame(zones_frame)
        zone_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(zone_btn_frame, text="Create Zone", command=self.create_zone, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(zone_btn_frame, text="Edit Zone", command=self.edit_zone, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(zone_btn_frame, text="Delete Zone", command=self.delete_zone, width=12).pack(side=tk.LEFT, padx=2)
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

        log_columns = ("timestamp", "zone", "sensor", "event")
        self.log_tree = ttk.Treeview(log_list_frame, columns=log_columns, show="headings", height=8)
        self.log_tree.heading("timestamp", text="Timestamp")
        self.log_tree.heading("zone", text="Zone")
        self.log_tree.heading("sensor", text="Sensor")
        self.log_tree.heading("event", text="Event")

        self.log_tree.column("timestamp", width=150)
        self.log_tree.column("zone", width=100)
        self.log_tree.column("sensor", width=100)
        self.log_tree.column("event", width=200)

        scrollbar_log = ttk.Scrollbar(log_list_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar_log.set)

        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)

        self.initialize_sample_data()
        self.refresh_zones_display()
        self.refresh_log_display()

    def initialize_sample_data(self):
        self.safety_zones = {
            1: {"name": "Front Door", "sensors": ["Door Sensor 1"], "armed": False},
            2: {"name": "Living Room", "sensors": ["Motion 1", "Window 1"], "armed": False},
            3: {"name": "Back Door", "sensors": ["Door Sensor 2"], "armed": False},
        }

    def arm_system(self):
        result = messagebox.askyesno("Arm System", "Are you sure you want to arm the system?")
        if result:
            self.system_armed = True
            self.system_mode = self.mode_var.get()
            self.status_label.config(text="ARMED", foreground="red")
            self.arm_btn.config(state=tk.DISABLED)
            self.disarm_btn.config(state=tk.NORMAL)
            self.add_log_entry("System", "System", "System Armed")
            self.app.update_status("System Armed - Mode: " + self.system_mode.title())

    def disarm_system(self):
        result = messagebox.askyesno("Disarm System", "Are you sure you want to disarm the system?")
        if result:
            self.system_armed = False
            self.status_label.config(text="DISARMED", foreground="green")
            self.arm_btn.config(state=tk.NORMAL)
            self.disarm_btn.config(state=tk.DISABLED)
            self.add_log_entry("System", "System", "System Disarmed")
            self.app.update_status("System Disarmed")

    def trigger_panic(self):
        result = messagebox.askyesno(
            "Panic Alarm",
            "This will trigger a panic alarm and call monitoring service. Continue?",
        )
        if result:
            self.add_log_entry("System", "Panic Button", "PANIC ALARM TRIGGERED")
            self.call_monitoring_service()
            messagebox.showwarning("Panic Alarm", "Panic alarm activated! Monitoring service notified.")

    def call_monitoring_service(self):
        self.add_log_entry("System", "Monitoring", "Monitoring Service Called")
        messagebox.showinfo(
            "Monitoring Service",
            "Monitoring service has been notified. Help is on the way.",
        )

    def create_zone(self):
        dialog = SafetyZoneDialog(self, None)
        if dialog.result:
            zone_id = max(self.safety_zones.keys(), default=0) + 1
            self.safety_zones[zone_id] = dialog.result
            self.refresh_zones_display()
            self.add_log_entry(f"Zone {zone_id}", "System", f"Zone '{dialog.result['name']}' created")

    def edit_zone(self):
        selected = self.zones_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a zone to edit")
            return

        item = self.zones_tree.item(selected[0])
        zone_id = int(item["values"][0])

        if zone_id in self.safety_zones:
            dialog = SafetyZoneDialog(self, self.safety_zones[zone_id])
            if dialog.result:
                self.safety_zones[zone_id] = dialog.result
                self.refresh_zones_display()
                self.add_log_entry(
                    f"Zone {zone_id}",
                    "System",
                    f"Zone '{dialog.result['name']}' updated",
                )

    def delete_zone(self):
        selected = self.zones_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a zone to delete")
            return

        item = self.zones_tree.item(selected[0])
        zone_id = int(item["values"][0])
        zone_name = item["values"][1]

        result = messagebox.askyesno("Delete Zone", f"Are you sure you want to delete zone '{zone_name}'?")
        if result:
            del self.safety_zones[zone_id]
            self.refresh_zones_display()
            self.add_log_entry(f"Zone {zone_id}", "System", f"Zone '{zone_name}' deleted")

    def toggle_zone(self):
        selected = self.zones_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a zone to arm/disarm")
            return

        item = self.zones_tree.item(selected[0])
        zone_id = int(item["values"][0])
        zone_name = item["values"][1]

        if zone_id in self.safety_zones:
            zone = self.safety_zones[zone_id]
            zone["armed"] = not zone["armed"]
            action = "Armed" if zone["armed"] else "Disarmed"
            self.refresh_zones_display()
            self.add_log_entry(f"Zone {zone_id}", "System", f"Zone '{zone_name}' {action.lower()}")

    def refresh_zones_display(self):
        for item in self.zones_tree.get_children():
            self.zones_tree.delete(item)

        for zone_id, zone in sorted(self.safety_zones.items()):
            status = "Armed" if zone["armed"] else "Disarmed"
            sensors = ", ".join(zone["sensors"])
            self.zones_tree.insert(
                "",
                tk.END,
                values=(zone_id, zone["name"], status, sensors),
            )

    def add_log_entry(self, zone, sensor, event):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.intrusion_log.insert(0, (timestamp, str(zone), str(sensor), event))
        if len(self.intrusion_log) > 100:
            self.intrusion_log = self.intrusion_log[:100]
        self.refresh_log_display()

    def refresh_log_display(self):
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        for entry in self.intrusion_log:
            self.log_tree.insert("", tk.END, values=entry)
