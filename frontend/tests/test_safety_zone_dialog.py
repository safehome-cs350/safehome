import tkinter as tk
from unittest.mock import patch

import pytest

from frontend.safety_zone_dialog import SafetyZoneDialog


class TestSafetyZoneDialog:
    def test_init_create_mode(self):
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None)

        assert dialog.title() == "Create Safety Zone"
        assert dialog.result == None

        root.destroy()

    def test_init_edit_mode(self):
        root = tk.Tk()
        root.withdraw()

        zone_data = {"name": "Test Zone", "sensors": ["Door Sensor 1"], "armed": False}

        dialog = SafetyZoneDialog(root, zone_data)

        assert dialog.title() == "Safety Zone"
        assert dialog.name_entry.get() == "Test Zone"

        root.destroy()

    def test_center_window(self):
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None)
        dialog.center_window()

        geometry = dialog.geometry()
        assert "x" in geometry
        assert "+" in geometry

        root.destroy()

    @patch("frontend.safety_zone_dialog.messagebox")
    def test_ok_clicked_empty_name(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None)
        dialog.ok_clicked()

        mock_messagebox.showerror.assert_called_once()
        assert dialog.result == None

        root.destroy()

    @patch("frontend.safety_zone_dialog.messagebox")
    def test_ok_clicked_no_sensors(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None)
        dialog.name_entry.insert(0, "Test Zone")
        dialog.ok_clicked()

        mock_messagebox.showerror.assert_called_once()
        assert dialog.result == None

        root.destroy()

    def test_ok_clicked_success(self):
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None)
        dialog.name_entry.insert(0, "Test Zone")
        dialog.sensor_listbox.selection_set(0)

        dialog.ok_clicked()

        assert dialog.result != None
        assert dialog.result["name"] == "Test Zone"
        assert len(dialog.result["sensors"]) > 0
        assert dialog.result["armed"] == False

        root.destroy()

    def test_cancel_clicked(self):
        root = tk.Tk()
        root.withdraw()

        dialog = SafetyZoneDialog(root, None)
        dialog.cancel_clicked()

        assert dialog.result == None

        root.destroy()
