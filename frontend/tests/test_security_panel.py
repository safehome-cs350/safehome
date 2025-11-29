"""Tests for security panel."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.security_panel import SecurityPanel


class TestSecurityPanel:
    """Test cases for SecurityPanel class."""

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_init(self, mock_api_client_class, mock_messagebox):
        """Test SecurityPanel initialization."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)

        assert panel.app == app
        assert not panel.system_armed
        assert isinstance(panel.safety_zones, dict)
        assert isinstance(panel.intrusion_log, list)

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_arm_system(self, mock_api_client_class, mock_messagebox):
        """Test arming the system."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.set_safehome_mode.return_value = {
            "current_mode": "away",
            "armed_devices": [1, 2],
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_messagebox.askyesno.return_value = True

        panel.arm_system()

        assert panel.system_armed
        assert panel.status_label.cget("text") == "ARMED"
        mock_messagebox.askyesno.assert_called_once()
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_disarm_system(self, mock_api_client_class, mock_messagebox):
        """Test disarming the system."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.disarm.return_value = {"message": "System disarmed"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
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
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_refresh_zones_display(self, mock_api_client_class, mock_messagebox):
        """Test refreshing zones display."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "device_ids": [1, 2],
                    "is_armed": False,
                }
            ]
        }
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)

        panel.refresh_zones_display()

        items = panel.zones_tree.get_children()
        assert len(items) == len(panel.safety_zones)

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_refresh_log_display(self, mock_api_client_class, mock_messagebox):
        """Test refreshing log display."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {
            "events": [
                {
                    "id": 1,
                    "timestamp": "2024-01-01T12:00:00",
                    "alarm_type": "intrusion",
                    "device_id": 1,
                    "location": "Living Room",
                    "description": "Test event",
                    "is_resolved": False,
                }
            ]
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)

        panel.refresh_log_display()

        items = panel.log_tree.get_children()
        assert len(items) == len(panel.intrusion_log)

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_trigger_panic(self, mock_api_client_class, mock_messagebox):
        """Test panic alarm trigger."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.panic_call.return_value = {
            "event_id": 1,
            "message": "Panic call initiated",
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_messagebox.askyesno.return_value = True

        panel.trigger_panic()

        mock_messagebox.askyesno.assert_called_once()
        mock_messagebox.showwarning.assert_called_once()
        mock_api_client.panic_call.assert_called_once()

        root.destroy()
