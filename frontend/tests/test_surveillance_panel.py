"""Tests for surveillance panel."""

import tkinter as tk
from pathlib import Path
from unittest.mock import Mock, patch

from frontend.surveillance_panel import SurveillancePanel


class TestSurveillancePanel:
    """Test cases for SurveillancePanel class."""

    @patch("frontend.surveillance_panel.APIClient")
    def test_init(self, mock_api_client_class):
        """Test SurveillancePanel initialization."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
            "cameras": [
                {
                    "camera_id": 1,
                    "name": "Camera 1",
                    "location": "Living Room",
                    "is_enabled": True,
                    "is_online": True,
                    "has_password": False,
                },
                {
                    "camera_id": 2,
                    "name": "Camera 2",
                    "location": "Kitchen",
                    "is_enabled": True,
                    "is_online": True,
                    "has_password": False,
                },
                {
                    "camera_id": 3,
                    "name": "Camera 3",
                    "location": "Bedroom",
                    "is_enabled": False,
                    "is_online": True,
                    "has_password": True,
                },
            ]
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        assert panel.app == app
        assert isinstance(panel.project_root, Path)
        assert len(panel.cameras) == 3
        assert panel.current_camera is None
        assert panel.current_zoom == 2
        assert panel.current_pan == 0

        root.destroy()

    @patch("frontend.surveillance_panel.APIClient")
    def test_refresh_camera_list(self, mock_api_client_class):
        """Test refreshing camera list."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
            "cameras": [
                {
                    "camera_id": 1,
                    "name": "Camera 1",
                    "location": "Living Room",
                    "is_enabled": True,
                    "is_online": True,
                    "has_password": False,
                },
            ]
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.refresh_camera_list()

        items = panel.camera_tree.get_children()
        assert len(items) == len(panel.cameras)

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_adjust_zoom(self, mock_api_client_class, mock_messagebox):
        """Test zoom adjustment."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client.control_camera_ptz.return_value = {
            "success": True,
            "zoom_level": 3,
            "pan_position": 0,
        }
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 0,
            "zoom_level": 3,
            "current_view_base64": None,
            "current_time": 0,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1
        panel.current_zoom = 2

        initial_zoom = panel.current_zoom
        panel.adjust_zoom(1)

        assert panel.current_zoom >= initial_zoom
        assert panel.current_zoom <= 9

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_reset_zoom(self, mock_api_client_class, mock_messagebox):
        """Test zoom reset."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client.control_camera_ptz.return_value = {
            "success": True,
            "zoom_level": 2,
            "pan_position": 0,
        }
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 0,
            "zoom_level": 2,
            "current_view_base64": None,
            "current_time": 0,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_zoom = 2.5
        panel.current_camera = 1

        panel.reset_zoom()

        assert panel.current_zoom == 2
        assert panel.zoom_label.cget("text") == "2"

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_adjust_pan(self, mock_api_client_class, mock_messagebox):
        """Test pan adjustment."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client.control_camera_ptz.return_value = {
            "success": True,
            "zoom_level": 2,
            "pan_position": 1,
        }
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 1,
            "zoom_level": 2,
            "current_view_base64": None,
            "current_time": 0,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1
        panel.current_pan = 0

        initial_pan = panel.current_pan

        panel.adjust_pan(1)

        assert panel.current_pan >= initial_pan
        assert panel.current_pan <= 5
        assert panel.current_pan >= -5

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_reset_pan(self, mock_api_client_class, mock_messagebox):
        """Test pan reset."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client.control_camera_ptz.return_value = {
            "success": True,
            "zoom_level": 2,
            "pan_position": 0,
        }
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 0,
            "zoom_level": 2,
            "current_view_base64": None,
            "current_time": 0,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_pan = 50
        panel.current_camera = 1

        panel.reset_pan()

        assert panel.current_pan == 0

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_enable_camera_no_selection(self, mock_api_client_class, mock_messagebox):
        """Test enabling camera with no selection."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.enable_camera()

        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_enable_camera_success(self, mock_api_client_class, mock_messagebox):
        """Test successful camera enable."""
        mock_api_client = Mock()
        # First call (in __init__) returns disabled camera
        # Second call (after enable) returns enabled camera
        mock_api_client.list_cameras.side_effect = [
            {
                "cameras": [
                    {
                        "camera_id": 3,
                        "name": "Camera 3",
                        "location": "Bedroom",
                        "is_enabled": False,
                        "is_online": True,
                        "has_password": False,
                    },
                ]
            },
            {
                "cameras": [
                    {
                        "camera_id": 3,
                        "name": "Camera 3",
                        "location": "Bedroom",
                        "is_enabled": True,
                        "is_online": True,
                        "has_password": False,
                    },
                ]
            },
        ]
        mock_api_client.enable_camera.return_value = {"message": "Camera enabled"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 3:
                panel.camera_tree.selection_set(item)
                break

        panel.enable_camera()

        assert panel.cameras[3]["is_enabled"]
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_disable_camera_success(self, mock_api_client_class, mock_messagebox):
        """Test successful camera disable."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.side_effect = [
            {
                "cameras": [
                    {
                        "camera_id": 1,
                        "name": "Camera 1",
                        "location": "Living Room",
                        "is_enabled": True,
                        "is_online": True,
                        "has_password": False,
                    },
                ]
            },
            {
                "cameras": [
                    {
                        "camera_id": 1,
                        "name": "Camera 1",
                        "location": "Living Room",
                        "is_enabled": False,
                        "is_online": True,
                        "has_password": False,
                    },
                ]
            },
        ]
        mock_api_client.disable_camera.return_value = {"message": "Camera disabled"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 1:
                panel.camera_tree.selection_set(item)
                break

        panel.disable_camera()

        assert not panel.cameras[1]["is_enabled"]
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_set_camera_password(
        self, mock_api_client_class, mock_messagebox, mock_simpledialog
    ):
        """Test setting camera password for camera without existing password."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
            "cameras": [
                {
                    "camera_id": 1,
                    "name": "Camera 1",
                    "location": "Living Room",
                    "is_enabled": True,
                    "is_online": True,
                    "has_password": False,
                },
            ]
        }
        mock_api_client.set_camera_password.return_value = {"message": "Password set"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        # Mock password prompts: new password, then confirm password
        mock_simpledialog.askstring.side_effect = ["newpass123", "newpass123"]

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 1:
                panel.camera_tree.selection_set(item)
                break

        panel.set_camera_password()

        # Should be called with new_password and None for old_password
        mock_api_client.set_camera_password.assert_called_once_with(
            1, "newpass123", None
        )
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_change_camera_password(
        self, mock_api_client_class, mock_messagebox, mock_simpledialog
    ):
        """Test changing camera password for camera with existing password."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
            "cameras": [
                {
                    "camera_id": 1,
                    "name": "Camera 1",
                    "location": "Living Room",
                    "is_enabled": True,
                    "is_online": True,
                    "has_password": True,
                },
            ]
        }
        mock_api_client.set_camera_password.return_value = {"message": "Password set"}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.cameras[1]["has_password"] = True
        # Mock password prompts: old password, new password, confirm password
        mock_simpledialog.askstring.side_effect = [
            "oldpass123",
            "newpass123",
            "newpass123",
        ]

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 1:
                panel.camera_tree.selection_set(item)
                break

        panel.set_camera_password()

        # Should be called with new_password and old_password
        mock_api_client.set_camera_password.assert_called_once_with(
            1, "newpass123", "oldpass123"
        )
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_delete_camera_password(
        self, mock_api_client_class, mock_messagebox, mock_simpledialog
    ):
        """Test deleting camera password."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
            "cameras": [
                {
                    "camera_id": 3,
                    "name": "Camera 3",
                    "location": "Bedroom",
                    "is_enabled": True,
                    "is_online": True,
                    "has_password": False,
                },
            ]
        }
        mock_api_client.delete_camera_password.return_value = {
            "message": "Password deleted"
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.cameras[3]["has_password"] = True
        mock_simpledialog.askstring.return_value = "test123"
        mock_messagebox.askyesno.return_value = True

        for item in panel.camera_tree.get_children():
            if int(panel.camera_tree.item(item)["tags"][0]) == 3:
                panel.camera_tree.selection_set(item)
                break

        panel.delete_camera_password()

        mock_api_client.delete_camera_password.assert_called_once_with(3, "test123")
        mock_messagebox.showinfo.assert_called_once()

        root.destroy()
