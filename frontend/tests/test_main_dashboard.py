"""Tests for main dashboard."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.main_dashboard import MainDashboard


class TestMainDashboard:
    """Test cases for MainDashboard class."""

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    @patch("frontend.surveillance_panel.APIClient")
    @patch("frontend.configuration_panel.APIClient")
    def test_init(
        self,
        mock_config_api,
        mock_surv_api,
        mock_security_api,
        mock_surv_messagebox,
        mock_security_messagebox,
    ):
        """Test MainDashboard initialization."""
        mock_surv_client = Mock()
        mock_surv_client.list_cameras.return_value = {"cameras": []}
        mock_surv_api.return_value = mock_surv_client

        mock_security_client = Mock()
        mock_security_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_security_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_security_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_security_client.view_intrusion_log.return_value = {"events": []}
        mock_security_api.return_value = mock_security_client

        mock_config_client = Mock()
        mock_config_client.get_config.return_value = {
            "password1": "",
            "password2": "",
            "master_password": "",
            "guest_password": "",
            "delay_time": 300,
            "phone_number": "",
        }
        mock_config_api.return_value = mock_config_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"

        dashboard = MainDashboard(root, app)

        assert dashboard.app == app
        assert hasattr(dashboard, "content_notebook")
        assert hasattr(dashboard, "status_label")

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    @patch("frontend.surveillance_panel.APIClient")
    @patch("frontend.configuration_panel.APIClient")
    def test_show_panel(
        self,
        mock_config_api,
        mock_surv_api,
        mock_security_api,
        mock_surv_messagebox,
        mock_security_messagebox,
    ):
        """Test panel switching."""
        mock_surv_client = Mock()
        mock_surv_client.list_cameras.return_value = {"cameras": []}
        mock_surv_api.return_value = mock_surv_client

        mock_security_client = Mock()
        mock_security_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_security_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_security_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_security_client.view_intrusion_log.return_value = {"events": []}
        mock_security_api.return_value = mock_security_client

        mock_config_client = Mock()
        mock_config_client.get_config.return_value = {
            "password1": "",
            "password2": "",
            "master_password": "",
            "guest_password": "",
            "delay_time": 300,
            "phone_number": "",
        }
        mock_config_api.return_value = mock_config_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"

        dashboard = MainDashboard(root, app)

        dashboard.show_panel("security")
        selected = dashboard.content_notebook.select()
        assert dashboard.content_notebook.index(selected) == 0

        dashboard.show_panel("surveillance")
        selected = dashboard.content_notebook.select()
        assert dashboard.content_notebook.index(selected) == 1

        dashboard.show_panel("configuration")
        selected = dashboard.content_notebook.select()
        assert dashboard.content_notebook.index(selected) == 2

        root.destroy()

    @patch("frontend.security_panel.messagebox")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.security_panel.APIClient")
    @patch("frontend.surveillance_panel.APIClient")
    @patch("frontend.configuration_panel.APIClient")
    def test_update_status(
        self,
        mock_config_api,
        mock_surv_api,
        mock_security_api,
        mock_surv_messagebox,
        mock_security_messagebox,
    ):
        """Test status bar update."""
        mock_surv_client = Mock()
        mock_surv_client.list_cameras.return_value = {"cameras": []}
        mock_surv_api.return_value = mock_surv_client

        mock_security_client = Mock()
        mock_security_client.get_safety_zones.return_value = {"safety_zones": []}
        mock_security_client.configure_safety_zone_interface.return_value = {
            "available_devices": []
        }
        mock_security_client.get_safehome_modes.return_value = {
            "current_mode": "away",
            "modes_configuration": {},
        }
        mock_security_client.view_intrusion_log.return_value = {"events": []}
        mock_security_api.return_value = mock_security_client

        mock_config_client = Mock()
        mock_config_client.get_config.return_value = {
            "password1": "",
            "password2": "",
            "master_password": "",
            "guest_password": "",
            "delay_time": 300,
            "phone_number": "",
        }
        mock_config_api.return_value = mock_config_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"

        dashboard = MainDashboard(root, app)

        dashboard.update_status("Test status")
        assert dashboard.status_label.cget("text") == "Test status"

        root.destroy()
