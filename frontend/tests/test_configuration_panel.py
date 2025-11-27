"""Tests for configuration panel."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from frontend.configuration_panel import (
    ConfigurationPanel,
    PasswordChangeDialog,
)


class TestConfigurationPanel:
    """Test cases for ConfigurationPanel class."""

    def test_init(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        assert panel.app == app
        assert "master_password" in panel.settings
        assert "guest_password" in panel.settings
        assert "delay_time" in panel.settings

        root.destroy()

    def test_turn_system_on(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        with patch(
            "frontend.configuration_panel.messagebox"
        ) as mock_messagebox:
            mock_messagebox.askyesno.return_value = True
            panel.turn_system_on()

            assert panel.system_power_var.get() == "ON"
            mock_messagebox.askyesno.assert_called_once()
            mock_messagebox.showinfo.assert_called_once()
            app.update_status.assert_called_once()

        root.destroy()

    def test_turn_system_off(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)

        with patch(
            "frontend.configuration_panel.messagebox"
        ) as mock_messagebox:
            mock_messagebox.askyesno.return_value = True
            panel.turn_system_off()

            assert panel.system_power_var.get() == "OFF"
            mock_messagebox.askyesno.assert_called_once()
            mock_messagebox.showinfo.assert_called_once()
            app.update_status.assert_called_once()

        root.destroy()

    def test_reset_system(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.settings["system_name"] = "Custom Name"

        with patch(
            "frontend.configuration_panel.messagebox"
        ) as mock_messagebox:
            mock_messagebox.askyesno.return_value = True
            panel.reset_system()

            assert panel.settings["system_name"] == "SafeHome System"
            assert panel.system_power_var.get() == "ON"
            mock_messagebox.showinfo.assert_called_once()
            app.update_status.assert_called_once()

        root.destroy()

    def test_save_settings(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.system_name_var.set("New System Name")
        panel.delay_time_var.set("45")
        panel.phone_number_var.set("555-9999")

        with patch(
            "frontend.configuration_panel.messagebox"
        ) as mock_messagebox:
            panel.save_settings()

            assert panel.settings["system_name"] == "New System Name"
            assert panel.settings["delay_time"] == 45
            assert panel.settings["phone_number"] == "555-9999"
            mock_messagebox.showinfo.assert_called_once()
            app.update_status.assert_called_once()

        root.destroy()

    def test_save_settings_invalid_delay(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        panel.delay_time_var.set("invalid")

        with patch(
            "frontend.configuration_panel.messagebox"
        ) as mock_messagebox:
            panel.save_settings()

            mock_messagebox.showerror.assert_called_once()
            app.update_status.assert_not_called()

        root.destroy()

    def test_cancel_changes(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.update_status = Mock()

        panel = ConfigurationPanel(root, app)
        original_name = panel.settings["system_name"]
        panel.system_name_var.set("Changed Name")

        with patch(
            "frontend.configuration_panel.messagebox"
        ) as mock_messagebox:
            panel.cancel_changes()

            assert panel.system_name_var.get() == original_name
            mock_messagebox.showinfo.assert_called_once()

        root.destroy()


class TestPasswordChangeDialog:
    """Test cases for PasswordChangeDialog class."""

    def test_init(self):
        root = tk.Tk()
        root.withdraw()

        dialog = PasswordChangeDialog(root, "Master Password")

        assert dialog.title() == "Change Master Password"
        assert dialog.result is None

        root.destroy()

    def test_center_window(self):
        root = tk.Tk()
        root.withdraw()

        dialog = PasswordChangeDialog(root, "Master Password")
        dialog.center_window()

        geometry = dialog.geometry()
        assert "x" in geometry
        assert "+" in geometry

        root.destroy()

    @patch("frontend.configuration_panel.messagebox")
    def test_ok_clicked_empty_fields(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()

        dialog = PasswordChangeDialog(root, "Master Password")
        dialog.ok_clicked()

        mock_messagebox.showerror.assert_called_once()
        assert dialog.result is None

        root.destroy()

    @patch("frontend.configuration_panel.messagebox")
    def test_ok_clicked_password_mismatch(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()

        dialog = PasswordChangeDialog(root, "Master Password")
        dialog.current_password_entry.insert(0, "current")
        dialog.new_password_entry.insert(0, "newpass")
        dialog.confirm_password_entry.insert(0, "different")

        dialog.ok_clicked()

        mock_messagebox.showerror.assert_called_once()
        assert dialog.result is None

        root.destroy()

    @patch("frontend.configuration_panel.messagebox")
    def test_ok_clicked_short_password(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()

        dialog = PasswordChangeDialog(root, "Master Password")
        dialog.current_password_entry.insert(0, "current")
        dialog.new_password_entry.insert(0, "abc")
        dialog.confirm_password_entry.insert(0, "abc")

        dialog.ok_clicked()

        mock_messagebox.showerror.assert_called_once()
        assert dialog.result is None

        root.destroy()

    def test_ok_clicked_success(self):
        root = tk.Tk()
        root.withdraw()

        dialog = PasswordChangeDialog(root, "Master Password")
        dialog.current_password_entry.insert(0, "current")
        dialog.new_password_entry.insert(0, "newpass123")
        dialog.confirm_password_entry.insert(0, "newpass123")

        dialog.ok_clicked()

        assert dialog.result == "newpass123"

        root.destroy()

    def test_cancel_clicked(self):
        root = tk.Tk()
        root.withdraw()

        dialog = PasswordChangeDialog(root, "Master Password")
        dialog.cancel_clicked()

        assert dialog.result is None

        root.destroy()
