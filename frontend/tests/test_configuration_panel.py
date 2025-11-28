"""Tests for configuration panel."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.configuration_panel import ConfigurationPanel


class TestConfigurationPanel:
    """Test cases for ConfigurationPanel class."""

    def test_init(self):
        """Test ConfigurationPanel initialization."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        assert panel.app == app
        assert "password1" in panel.settings
        assert "password2" in panel.settings
        assert "master_password" in panel.settings
        assert "guest_password" in panel.settings
        assert "delay_time" in panel.settings
        assert "phone_number" in panel.settings

        root.destroy()

    def test_turn_system_on(self):
        """Test turning system on."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            mock_messagebox.askyesno.return_value = True
            with patch.object(panel.api_client, "power_on") as mock_power_on:
                panel.turn_system_on()

                mock_power_on.assert_called_once_with("homeowner1")
                assert panel.system_power_var.get() == "ON"
                mock_messagebox.askyesno.assert_called_once()
                mock_messagebox.showinfo.assert_called_once()
                app.update_status.assert_called_once()

        root.destroy()

    def test_turn_system_off(self):
        """Test turning system off."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            mock_messagebox.askyesno.return_value = True
            with patch.object(panel.api_client, "power_off") as mock_power_off:
                panel.turn_system_off()

                mock_power_off.assert_called_once_with("homeowner1")
                assert panel.system_power_var.get() == "OFF"
                mock_messagebox.askyesno.assert_called_once()
                mock_messagebox.showinfo.assert_called_once()
                app.update_status.assert_called_once()

        root.destroy()

    def test_reset_system(self):
        """Test system reset."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            mock_messagebox.askyesno.return_value = True
            with patch.object(panel.api_client, "config") as mock_config:
                with patch.object(panel, "load_config") as mock_load:
                    panel.reset_system()

                    mock_config.assert_called_once()
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()
                    app.update_status.assert_called_once()

        root.destroy()

    def test_save_settings(self):
        """Test saving settings."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("600")
        panel.phone_number_var.set("555-9999")

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            with patch.object(panel.api_client, "config") as mock_config:
                with patch.object(panel, "load_config") as mock_load:
                    panel.save_settings()

                    mock_config.assert_called_once()
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()
                    app.update_status.assert_called_once()

        root.destroy()

    def test_save_settings_invalid_delay(self):
        """Test saving settings with invalid delay time."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("invalid")

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            panel.save_settings()

            mock_messagebox.showerror.assert_called_once()
            app.update_status.assert_not_called()

        root.destroy()
