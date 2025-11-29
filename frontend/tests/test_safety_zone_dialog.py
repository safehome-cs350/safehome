"""Tests for safety zone dialog."""

import tkinter as tk
from unittest.mock import patch

from frontend.safety_zone_dialog import SafetyZoneDialog


class TestSafetyZoneDialog:
    """Test cases for SafetyZoneDialog class."""

    @patch("frontend.safety_zone_dialog.SafetyZoneDialog.grab_set")
    def test_init_create_mode(self, mock_grab):
        """Test dialog initialization in create mode."""
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None, available_devices=[])

        assert dialog.title() == "Create Safety Zone"
        assert dialog.result is None

        root.destroy()

    @patch("frontend.safety_zone_dialog.SafetyZoneDialog.grab_set")
    def test_init_edit_mode(self, mock_grab):
        """Test dialog initialization in edit mode."""
        root = tk.Tk()
        root.withdraw()

        zone_data = {
            "name": "Test Zone",
            "device_ids": [1],
        }

        dialog = SafetyZoneDialog(root, zone_data, available_devices=[{"id": 1, "type": "sensor"}])

        assert dialog.title() == "Edit Safety Zone"
        assert dialog.name_entry.get() == "Test Zone"

        root.destroy()

    @patch("frontend.safety_zone_dialog.SafetyZoneDialog.grab_set")
    def test_center_window(self, mock_grab):
        """Test window centering."""
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None, available_devices=[])
        dialog.center_window()

        geometry = dialog.geometry()
        assert "x" in geometry
        assert "+" in geometry

        root.destroy()

    @patch("frontend.safety_zone_dialog.SafetyZoneDialog.grab_set")
    @patch("frontend.safety_zone_dialog.messagebox")
    def test_ok_clicked_empty_name(self, mock_messagebox, mock_grab):
        """Test OK click with empty name."""
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None, available_devices=[])
        dialog.ok_clicked()

        mock_messagebox.showerror.assert_called_once()
        assert dialog.result is None

        root.destroy()

    @patch("frontend.safety_zone_dialog.SafetyZoneDialog.grab_set")
    @patch("frontend.safety_zone_dialog.messagebox")
    def test_ok_clicked_no_sensors(self, mock_messagebox, mock_grab):
        """Test OK click with no sensors selected."""
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None, available_devices=[{"id": 1, "type": "sensor"}])
        dialog.name_entry.insert(0, "Test Zone")
        dialog.ok_clicked()

        mock_messagebox.showerror.assert_called_once()
        assert dialog.result is None

        root.destroy()

    @patch("frontend.safety_zone_dialog.SafetyZoneDialog.grab_set")
    def test_ok_clicked_success(self, mock_grab):
        """Test successful zone creation."""
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None, available_devices=[{"id": 1, "type": "sensor"}])
        dialog.name_entry.insert(0, "Test Zone")
        dialog.device_listbox.selection_set(0)

        dialog.ok_clicked()

        assert dialog.result is not None
        assert dialog.result["name"] == "Test Zone"
        assert len(dialog.result["device_ids"]) > 0

        root.destroy()

    @patch("frontend.safety_zone_dialog.SafetyZoneDialog.grab_set")
    def test_cancel_clicked(self, mock_grab):
        """Test cancel button click."""
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None, available_devices=[])
        dialog.cancel_clicked()

        assert dialog.result is None

        root.destroy()
