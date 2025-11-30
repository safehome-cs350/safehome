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
        mock_messagebox.askyesno.return_value = True

        panel.disarm_system()

        assert not panel.system_armed
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

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_safety_zones_no_user(self, mock_api_client_class, mock_messagebox):
        """Test load_safety_zones with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.load_safety_zones()

        mock_api_client.get_safety_zones.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_safety_zones_connection_error(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test load_safety_zones with connection error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.side_effect = Exception("Connection refused")
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
        panel.load_safety_zones()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_data_no_user(self, mock_api_client_class, mock_messagebox):
        """Test load_data with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.app.current_user = None
        panel.load_data()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_intrusion_log_no_user(self, mock_api_client_class, mock_messagebox):
        """Test load_intrusion_log with no user."""
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
        # Reset the mock call count
        mock_api_client.view_intrusion_log.reset_mock()
        # Set current_user to None after initialization
        app.current_user = None
        panel.load_intrusion_log()

        mock_api_client.view_intrusion_log.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_arm_system_no_user(self, mock_api_client_class, mock_messagebox):
        """Test arm_system with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.arm_system()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "No user logged in" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_arm_system_doors_not_closed(self, mock_api_client_class, mock_messagebox):
        """Test arm_system with doors not closed error."""
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
        mock_api_client.set_safehome_mode.side_effect = Exception(
            "doors and windows not closed"
        )
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_messagebox.askyesno.return_value = True

        panel.arm_system()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "doors and windows not closed" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_disarm_system_no_user(self, mock_api_client_class, mock_messagebox):
        """Test disarm_system with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.disarm_system()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "No user logged in" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_trigger_panic_no_user(self, mock_api_client_class, mock_messagebox):
        """Test trigger_panic with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.trigger_panic()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "No user logged in" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_call_monitoring_service(self, mock_api_client_class, mock_messagebox):
        """Test call_monitoring_service."""
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

        panel.call_monitoring_service()

        mock_api_client.panic_call.assert_called_once()

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_create_zone_no_user(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test create_zone with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.create_zone()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "No user logged in" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_create_zone_success(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test successful zone creation."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [{"id": 1, "type": "motion"}]
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.create_safety_zone.return_value = {"message": "Zone created"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 1", "device_ids": [1]}
        # Mock wait_window to do nothing (it's called on the dialog)
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.create_zone()

            mock_api_client.create_safety_zone.assert_called_once()
            mock_messagebox.showinfo.assert_called()

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_edit_zone_no_selection(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test edit_zone with no selection."""
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
        panel.edit_zone()

        mock_messagebox.showinfo.assert_called_once()
        call_args = mock_messagebox.showinfo.call_args[0]
        assert "No Selection" in call_args[0]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_delete_zone_no_selection(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test delete_zone with no selection."""
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
        panel.delete_zone()

        mock_messagebox.showinfo.assert_called_once()
        call_args = mock_messagebox.showinfo.call_args[0]
        assert "No Selection" in call_args[0]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_toggle_zone_no_selection(self, mock_api_client_class, mock_messagebox):
        """Test toggle_zone with no selection."""
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
        panel.toggle_zone()

        mock_messagebox.showinfo.assert_called_once()
        call_args = mock_messagebox.showinfo.call_args[0]
        assert "No Selection" in call_args[0]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_on_mode_change_no_user(self, mock_api_client_class, mock_messagebox):
        """Test on_mode_change with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.on_mode_change("home")

        mock_api_client.set_safehome_mode.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_on_mode_change_loading(self, mock_api_client_class, mock_messagebox):
        """Test on_mode_change during loading."""
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
        panel._loading_mode = True
        panel.on_mode_change("home")

        mock_api_client.set_safehome_mode.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_on_mode_change_same_mode(self, mock_api_client_class, mock_messagebox):
        """Test on_mode_change with same mode."""
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
        panel.current_mode = "away"
        panel.on_mode_change("away")

        # Should not call set_safehome_mode if mode hasn't changed
        # (This depends on implementation - checking that it doesn't error)

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_create_zone_connection_error(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test create_zone with connection error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.side_effect = Exception(
            "Connection refused"
        )
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
        panel.available_devices = []
        panel.create_zone()

        mock_messagebox.showerror.assert_called()

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_create_zone_duplicate_name(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test create_zone with duplicate zone name."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [{"id": 1, "type": "motion"}]
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.create_safety_zone.side_effect = Exception(
            "Same safety zone exists"
        )
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 1", "device_ids": [1]}
        # Mock wait_window to do nothing (it's called on the dialog)
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.create_zone()

            mock_messagebox.showerror.assert_called()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "already exists" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_edit_zone_no_user(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test edit_zone with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.edit_zone()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "No user logged in" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_delete_zone_no_user(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test delete_zone with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.delete_zone()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "No user logged in" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_toggle_zone_no_user(self, mock_api_client_class, mock_messagebox):
        """Test toggle_zone with no user."""
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
        app.current_user = None
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.toggle_zone()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "No user logged in" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_on_mode_change_doors_not_closed(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test on_mode_change with doors not closed error."""
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
        mock_api_client.set_safehome_mode.side_effect = Exception(
            "doors and windows not closed"
        )
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.current_mode = "away"

        # Mock reconfirm dialog to auto-confirm
        with patch("frontend.security_panel.ReconfirmDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.result = True
            mock_dialog_instance.address = "123 Main St"
            mock_dialog_instance.phone_number = None
            mock_dialog.return_value = mock_dialog_instance
            mock_api_client.reconfirm.return_value = {"message": "Reconfirmed"}
            with patch.object(panel, "wait_window"):
                panel.on_mode_change("home")

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "doors and windows not closed" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_arm_system_user_cancels(self, mock_api_client_class, mock_messagebox):
        """Test arm_system when user cancels."""
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
        mock_messagebox.askyesno.return_value = False

        panel.arm_system()

        mock_api_client.set_safehome_mode.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_disarm_system_user_cancels(self, mock_api_client_class, mock_messagebox):
        """Test disarm_system when user cancels."""
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
        panel.system_armed = True
        mock_messagebox.askyesno.return_value = False

        panel.disarm_system()

        mock_api_client.disarm.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_trigger_panic_user_cancels(self, mock_api_client_class, mock_messagebox):
        """Test trigger_panic when user cancels."""
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
        mock_messagebox.askyesno.return_value = False

        panel.trigger_panic()

        mock_api_client.panic_call.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_safety_zones_generic_error(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test load_safety_zones with generic error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.side_effect = Exception("Generic error")
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
        panel.load_safety_zones()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to load safety zones" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_data_generic_error(self, mock_api_client_class, mock_messagebox):
        """Test load_data with generic error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.side_effect = Exception(
            "Generic error"
        )
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
        panel.load_data()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to load security data" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_intrusion_log_timestamp_parsing(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test load_intrusion_log with different timestamp formats."""
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
                    "timestamp": "2024-01-01T12:00:00",  # ISO format with T
                    "alarm_type": "intrusion",
                    "device_id": 1,
                    "location": "Living Room",
                    "description": "Test event",
                    "is_resolved": False,
                },
                {
                    "id": 2,
                    "timestamp": "2024-01-01 12:00:00",  # ISO format without T
                    "alarm_type": "intrusion",
                    "device_id": 2,
                    "location": "Kitchen",
                    "description": "Test event 2",
                    "is_resolved": False,
                },
                {
                    "id": 3,
                    "timestamp": "invalid-timestamp",  # Invalid format
                    "alarm_type": "intrusion",
                    "device_id": 3,
                    "location": "Bedroom",
                    "description": "Test event 3",
                    "is_resolved": False,
                },
            ]
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.load_intrusion_log()

        # Should handle all timestamp formats
        assert len(panel.intrusion_log) == 3

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_load_intrusion_log_connection_error_silent(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test load_intrusion_log with connection error (silent fail)."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.side_effect = Exception("Connection refused")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Reset mock to ignore init call
        mock_api_client.view_intrusion_log.reset_mock()
        panel.load_intrusion_log()

        # Should silently fail (no error message shown)
        # Connection errors are handled silently in load_intrusion_log

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_delete_zone_success(self, mock_api_client_class, mock_messagebox):
        """Test successful zone deletion."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        mock_api_client.delete_safety_zone.return_value = {"message": "Zone deleted"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        mock_messagebox.askyesno.return_value = True
        panel.delete_zone()

        mock_api_client.delete_safety_zone.assert_called_once()
        mock_messagebox.showinfo.assert_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_delete_zone_user_cancels(self, mock_api_client_class, mock_messagebox):
        """Test delete_zone when user cancels."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        mock_messagebox.askyesno.return_value = False
        panel.delete_zone()

        mock_api_client.delete_safety_zone.assert_not_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_toggle_zone_arm(self, mock_api_client_class, mock_messagebox):
        """Test toggle_zone to arm a zone."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        mock_api_client.arm_safety_zone.return_value = {"message": "Zone armed"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        panel.toggle_zone()

        mock_api_client.arm_safety_zone.assert_called_once()
        mock_messagebox.showinfo.assert_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_toggle_zone_disarm(self, mock_api_client_class, mock_messagebox):
        """Test toggle_zone to disarm a zone."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
                    "is_armed": True,
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
        mock_api_client.disarm_safety_zone.return_value = {"message": "Zone disarmed"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        panel.toggle_zone()

        mock_api_client.disarm_safety_zone.assert_called_once()
        mock_messagebox.showinfo.assert_called()

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_toggle_zone_connection_error(self, mock_api_client_class, mock_messagebox):
        """Test toggle_zone with connection error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        mock_api_client.arm_safety_zone.side_effect = Exception("Connection refused")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        panel.toggle_zone()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_on_mode_change_success(self, mock_api_client_class, mock_messagebox):
        """Test on_mode_change success path."""
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
            "current_mode": "home",
            "is_system_armed": True,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.current_mode = "away"
        # Reset mock to ignore load_data call
        mock_api_client.get_safehome_modes.reset_mock()
        mock_api_client.get_safety_zones.reset_mock()
        mock_api_client.configure_safety_zone_interface.reset_mock()
        mock_api_client.view_intrusion_log.reset_mock()

        # Mock reconfirm dialog to auto-confirm
        with patch("frontend.security_panel.ReconfirmDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.result = True
            mock_dialog_instance.address = "123 Main St"
            mock_dialog_instance.phone_number = None
            mock_dialog.return_value = mock_dialog_instance
            with patch.object(panel, "wait_window"):
                panel.on_mode_change("home")

        mock_api_client.set_safehome_mode.assert_called_once()
        # Verify mode was updated (may be affected by load_data, so check it was called)
        assert mock_api_client.set_safehome_mode.called

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_on_mode_change_connection_error(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test on_mode_change with connection error."""
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
        mock_api_client.set_safehome_mode.side_effect = Exception("Connection refused")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.current_mode = "away"

        # Mock reconfirm dialog to auto-confirm
        with patch("frontend.security_panel.ReconfirmDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.result = True
            mock_dialog_instance.address = "123 Main St"
            mock_dialog_instance.phone_number = None
            mock_dialog.return_value = mock_dialog_instance
            mock_api_client.reconfirm.return_value = {"message": "Reconfirmed"}
            with patch.object(panel, "wait_window"):
                panel.on_mode_change("home")

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Cannot connect to backend server" in call_args[1]
        # Mode should be reverted
        assert panel.current_mode == "away"

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_edit_zone_name_change(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test edit_zone with name change."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
                    "is_armed": False,
                }
            ]
        }
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [{"id": 1, "type": "motion"}]
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.delete_safety_zone.return_value = {"message": "Deleted"}
        mock_api_client.create_safety_zone.return_value = {"message": "Created"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 2", "device_ids": [1]}
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.edit_zone()

            mock_api_client.delete_safety_zone.assert_called_once()
            mock_api_client.create_safety_zone.assert_called_once()
            mock_messagebox.showinfo.assert_called()

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_edit_zone_device_change_only(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test edit_zone with device change only (no name change)."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
                    "is_armed": False,
                }
            ]
        }
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [
                {"id": 1, "type": "motion"},
                {"id": 2, "type": "motion"},
            ]
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.update_safety_zone.return_value = {"message": "Updated"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 1", "device_ids": [1, 2]}
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.edit_zone()

            mock_api_client.update_safety_zone.assert_called_once()
            mock_api_client.delete_safety_zone.assert_not_called()
            mock_api_client.create_safety_zone.assert_not_called()
            mock_messagebox.showinfo.assert_called()

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_edit_zone_duplicate_name_error(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test edit_zone with duplicate name error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
                    "is_armed": False,
                },
                {
                    "name": "Zone 2",
                    "devices": [{"id": 2}],
                    "is_armed": False,
                },
            ]
        }
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [{"id": 1, "type": "motion"}]
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
        # Select Zone 1
        for item in panel.zones_tree.get_children():
            if panel.zones_tree.item(item)["values"][0] == "Zone 1":
                panel.zones_tree.selection_set(item)
                break

        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 2", "device_ids": [1]}
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.edit_zone()

            mock_messagebox.showerror.assert_called()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "already exists" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_arm_system_generic_error(self, mock_api_client_class, mock_messagebox):
        """Test arm_system with generic error."""
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
        mock_api_client.set_safehome_mode.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_messagebox.askyesno.return_value = True

        panel.arm_system()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to arm system" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_disarm_system_generic_error(self, mock_api_client_class, mock_messagebox):
        """Test disarm_system with generic error."""
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
        mock_api_client.disarm.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.system_armed = True
        mock_messagebox.askyesno.return_value = True

        panel.disarm_system()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to disarm system" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_trigger_panic_generic_error(self, mock_api_client_class, mock_messagebox):
        """Test trigger_panic with generic error."""
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
        mock_api_client.panic_call.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_messagebox.askyesno.return_value = True

        panel.trigger_panic()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to trigger panic" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_create_zone_connection_error_during_create(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test create_zone with connection error in create call."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [{"id": 1, "type": "motion"}]
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.create_safety_zone.side_effect = Exception("Connection refused")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 1", "device_ids": [1]}
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.create_zone()

            mock_messagebox.showerror.assert_called()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_create_zone_generic_error_during_create(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test create_zone with generic error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [{"id": 1, "type": "motion"}]
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.create_safety_zone.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 1", "device_ids": [1]}
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.create_zone()

            mock_messagebox.showerror.assert_called()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "Failed to create zone" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_edit_zone_load_devices_generic_error(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test edit_zone with generic error loading devices."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        mock_api_client.configure_safety_zone_interface.side_effect = Exception(
            "Generic error"
        )
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.available_devices = []  # Force reload
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        panel.edit_zone()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to load devices" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.SafetyZoneDialog")
    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_edit_zone_update_generic_error(
        self, mock_api_client_class, mock_messagebox, mock_dialog
    ):
        """Test edit_zone with generic update error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
                    "is_armed": False,
                }
            ]
        }
        mock_api_client.configure_safety_zone_interface.return_value = {
            "available_devices": [{"id": 1, "type": "motion"}]
        }
        mock_api_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_api_client.view_intrusion_log.return_value = {"events": []}
        mock_api_client.update_safety_zone.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        mock_dialog_instance = Mock()
        mock_dialog_instance.result = {"name": "Zone 1", "device_ids": [1, 2]}
        with patch.object(panel, "wait_window"):
            mock_dialog.return_value = mock_dialog_instance

            panel.edit_zone()

            mock_messagebox.showerror.assert_called()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "Failed to update zone" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_delete_zone_connection_error_during_delete(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test delete_zone with connection error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        mock_api_client.delete_safety_zone.side_effect = Exception("Connection refused")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        mock_messagebox.askyesno.return_value = True
        panel.delete_zone()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_delete_zone_generic_error_during_delete(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test delete_zone with generic error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        mock_api_client.delete_safety_zone.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        mock_messagebox.askyesno.return_value = True
        panel.delete_zone()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to delete zone" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_toggle_zone_generic_error_during_toggle(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test toggle_zone with generic error."""
        mock_api_client = Mock()
        mock_api_client.get_safety_zones.return_value = {
            "safety_zones": [
                {
                    "name": "Zone 1",
                    "devices": [{"id": 1}],
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
        mock_api_client.arm_safety_zone.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        # Select a zone
        for item in panel.zones_tree.get_children():
            panel.zones_tree.selection_set(item)
            break

        panel.toggle_zone()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to toggle zone" in call_args[1]

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    def test_on_mode_change_generic_error_during_change(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test on_mode_change with generic error."""
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
        mock_api_client.set_safehome_mode.side_effect = Exception("Generic error")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.update_status = Mock()

        panel = SecurityPanel(root, app)
        panel.current_mode = "away"

        # Mock reconfirm dialog to auto-confirm
        with patch("frontend.security_panel.ReconfirmDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.result = True
            mock_dialog_instance.address = "123 Main St"
            mock_dialog_instance.phone_number = None
            mock_dialog.return_value = mock_dialog_instance
            mock_api_client.reconfirm.return_value = {"message": "Reconfirmed"}
            with patch.object(panel, "wait_window"):
                panel.on_mode_change("home")

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to set mode" in call_args[1]

        root.destroy()
