"""Tests for security panel."""

import tkinter as tk
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from frontend.security_panel import SecurityPanel


class TestSecurityPanel:
    """Test cases for SecurityPanel class."""

    def test_init(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)

        assert panel.app == app
        assert not panel.system_armed
        assert panel.system_mode == "disarmed"
        assert isinstance(panel.safety_zones, dict)
        assert isinstance(panel.intrusion_log, list)

        root.destroy()

    def test_initialize_sample_data(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)

        assert len(panel.safety_zones) == 3
        assert 1 in panel.safety_zones
        assert 2 in panel.safety_zones
        assert 3 in panel.safety_zones

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    def test_arm_system(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_messagebox.askyesno.return_value = True

        panel.arm_system()

        assert panel.system_armed
        assert panel.status_label.cget("text") == "ARMED"
        mock_messagebox.askyesno.assert_called_once()
        app.update_status.assert_called_once()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    def test_disarm_system(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.system_armed = True
        panel.arm_btn.config(state=tk.DISABLED)
        panel.disarm_btn.config(state=tk.NORMAL)
        mock_messagebox.askyesno.return_value = True

        panel.disarm_system()

        assert not panel.system_armed
        assert panel.status_label.cget("text") == "DISARMED"
        mock_messagebox.askyesno.assert_called_once()
        app.update_status.assert_called_once()

        root.destroy()

    def test_add_log_entry(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        initial_count = len(panel.intrusion_log)

        panel.add_log_entry("Zone 1", "Sensor 1", "Test event")

        assert len(panel.intrusion_log) == initial_count + 1
        assert panel.intrusion_log[0][2] == "Sensor 1"
        assert panel.intrusion_log[0][3] == "Test event"

        root.destroy()

    def test_refresh_zones_display(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)

        panel.refresh_zones_display()

        items = panel.zones_tree.get_children()
        assert len(items) == len(panel.safety_zones)

        root.destroy()

    def test_refresh_log_display(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.add_log_entry("Zone 1", "Sensor 1", "Test event")

        panel.refresh_log_display()

        items = panel.log_tree.get_children()
        assert len(items) == len(panel.intrusion_log)

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    def test_trigger_panic(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_messagebox.askyesno.return_value = True

        panel.trigger_panic()

        assert len(panel.intrusion_log) > 0
        panic_entries = [
            entry for entry in panel.intrusion_log if "PANIC" in entry[3]
        ]
        assert len(panic_entries) > 0
        mock_messagebox.askyesno.assert_called_once()
        mock_messagebox.showwarning.assert_called_once()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    def test_call_monitoring_service(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = SecurityPanel(root, app)

        panel.call_monitoring_service()

        assert len(panel.intrusion_log) > 0
        assert "Monitoring" in panel.intrusion_log[0][3]
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()
