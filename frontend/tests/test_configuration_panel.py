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

    def test_save_settings_no_user(self):
        """Test saving settings without logged in user."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = None
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            panel.save_settings()

            mock_messagebox.showerror.assert_called_once_with(
                "Error", "No user logged in"
            )

        root.destroy()

    def test_save_settings_delay_too_small(self):
        """Test saving settings with delay time less than 0."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("-1")

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            panel.save_settings()

            mock_messagebox.showerror.assert_called_once()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "Delay time must be at least 0" in call_args[1]

        root.destroy()

    def test_save_settings_connection_error(self):
        """Test saving settings with connection error."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("600")

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            with patch.object(panel.api_client, "config") as mock_config:
                mock_config.side_effect = Exception("Connection refused")
                panel.save_settings()

                mock_messagebox.showerror.assert_called()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    def test_save_settings_400_error(self):
        """Test saving settings with 400 error (delay time)."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("600")

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            with patch.object(panel.api_client, "config") as mock_config:
                mock_config.side_effect = Exception(
                    "400: Delay time must be at least 0"
                )
                panel.save_settings()

                mock_messagebox.showerror.assert_called_once_with(
                    "Error", "Delay time must be at least 0 seconds"
                )

        root.destroy()

    def test_save_settings_generic_error(self):
        """Test saving settings with generic error."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("600")

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            with patch.object(panel.api_client, "config") as mock_config:
                mock_config.side_effect = Exception("Some other error")
                panel.save_settings()

                mock_messagebox.showerror.assert_called()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to save settings" in call_args[1]

        root.destroy()

    def test_save_settings_with_password_changes(self):
        """Test saving settings with password changes."""
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "homeowner1"
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("600")
        panel.password1_var.set("newpass1")
        panel.password2_var.set("newpass2")
        panel.master_password_var.set("newmaster")
        panel.guest_password_var.set("newguest")

        with patch("frontend.configuration_panel.messagebox") as mock_messagebox:
            with patch.object(panel.api_client, "config") as mock_config:
                mock_config.return_value = {"message": "Settings saved"}
                with patch.object(panel, "load_config") as mock_load:
                    panel.save_settings()

                    # Verify config was called with password parameters
                    call_kwargs = mock_config.call_args[1]
                    assert call_kwargs["password1"] == "newpass1"
                    assert call_kwargs["password2"] == "newpass2"
                    assert call_kwargs["master_password"] == "newmaster"
                    assert call_kwargs["guest_password"] == "newguest"
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()
