"""Tests for surveillance panel."""

import tkinter as tk
from pathlib import Path
from unittest.mock import Mock, patch

from frontend.surveillance_panel import SurveillancePanel


class TestSurveillancePanel:
    """Test cases for SurveillancePanel class."""

    def test_init(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        assert panel.app == app
        assert isinstance(panel.project_root, Path)
        assert len(panel.cameras) == 3
        assert panel.current_camera is None
        assert panel.zoom_level == 1.0

        root.destroy()

    def test_refresh_camera_list(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.refresh_camera_list()

        items = panel.camera_tree.get_children()
        assert len(items) == len(panel.cameras)

        root.destroy()

    def test_adjust_zoom(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1

        initial_zoom = panel.zoom_level
        panel.adjust_zoom(1.2)

        assert panel.zoom_level > initial_zoom
        assert panel.zoom_level <= 5.0

        root.destroy()

    def test_reset_zoom(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.zoom_level = 2.5
        panel.current_camera = 1

        panel.reset_zoom()

        assert panel.zoom_level == 1.0
        assert panel.zoom_label.cget("text") == "1.0x"

        root.destroy()

    def test_adjust_pan(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1

        initial_x = panel.pan_x
        initial_y = panel.pan_y

        panel.adjust_pan(10, 20)

        assert panel.pan_x == initial_x + 10
        assert panel.pan_y == initial_y + 20
        assert panel.pan_x <= 100
        assert panel.pan_x >= -100

        root.destroy()

    def test_reset_pan(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.pan_x = 50
        panel.pan_y = -30
        panel.current_camera = 1

        panel.reset_pan()

        assert panel.pan_x == 0
        assert panel.pan_y == 0

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    def test_enable_camera_no_selection(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.enable_camera()

        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    def test_enable_camera_success(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 3:
                panel.camera_tree.selection_set(item)
                break

        panel.enable_camera()

        assert panel.cameras[3]["enabled"]
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    def test_disable_camera_success(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 1:
                panel.camera_tree.selection_set(item)
                break

        panel.disable_camera()

        assert not panel.cameras[1]["enabled"]
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    def test_set_camera_password(self, mock_messagebox, mock_simpledialog):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        mock_simpledialog.askstring.return_value = "newpass123"

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 1:
                panel.camera_tree.selection_set(item)
                break

        panel.set_camera_password()

        assert panel.cameras[1]["password"] == "newpass123"
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    def test_delete_camera_password(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.cameras[3]["password"] = "testpass"
        mock_messagebox.askyesno.return_value = True

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 3:
                panel.camera_tree.selection_set(item)
                break

        panel.delete_camera_password()

        assert panel.cameras[3]["password"] is None
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()
