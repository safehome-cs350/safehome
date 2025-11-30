"""Additional tests for security panel to reach 100% coverage."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.security_panel import SecurityPanel


class TestSecurityPanelAdditional:
    """Additional test cases for SecurityPanel class to reach 100% coverage."""

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
        panel.mode_var.set("home")

        panel.on_mode_change()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Failed to set mode" in call_args[1]

        root.destroy()
