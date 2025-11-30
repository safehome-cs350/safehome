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

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_cameras_connection_error(self, mock_api_client_class, mock_messagebox):
        """Test load_cameras with connection error."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.side_effect = Exception("Connection refused")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_on_canvas_resize(self, mock_api_client_class, mock_messagebox):
        """Test canvas resize event."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
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
        panel.current_camera = 1
        panel.camera_passwords[1] = "testpass"

        event = Mock()
        event.width = 640
        event.height = 480

        panel.on_canvas_resize(event)

        mock_api_client.get_camera_view.assert_called_once_with(1, password="testpass")

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_on_camera_select_disabled(self, mock_api_client_class, mock_messagebox, mock_simpledialog):
        """Test camera selection with disabled camera."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
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
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            panel.on_camera_select(None)
            break

        mock_messagebox.showinfo.assert_called_once()
        call_args = mock_messagebox.showinfo.call_args[0]
        assert "Camera Disabled" in call_args[0]

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_on_camera_select_offline(self, mock_api_client_class, mock_messagebox, mock_simpledialog):
        """Test camera selection with offline camera."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
            "cameras": [
                {
                    "camera_id": 1,
                    "name": "Camera 1",
                    "location": "Living Room",
                    "is_enabled": True,
                    "is_online": False,
                    "has_password": False,
                },
            ]
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            panel.on_camera_select(None)
            break

        mock_messagebox.showwarning.assert_called_once()
        call_args = mock_messagebox.showwarning.call_args[0]
        assert "Camera Offline" in call_args[0]

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_on_camera_select_password_cancel(self, mock_api_client_class, mock_messagebox, mock_simpledialog):
        """Test camera selection with password prompt cancelled."""
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
        mock_simpledialog.askstring.return_value = None
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            panel.on_camera_select(None)
            break

        mock_api_client.get_camera_view.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_camera_view_400_error(self, mock_api_client_class, mock_messagebox):
        """Test load_camera_view with 400 error."""
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
        mock_api_client.get_camera_view.side_effect = Exception("400: Camera is disabled")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1

        panel.load_camera_view(1)

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Camera is disabled" in call_args[1]

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_camera_view_401_password_required(self, mock_api_client_class, mock_messagebox):
        """Test load_camera_view with 401 password required error."""
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
        mock_api_client.get_camera_view.side_effect = Exception("401: Password required")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1
        panel.camera_passwords[1] = "wrongpass"

        panel.load_camera_view(1, password="wrongpass")

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Password required" in call_args[1]

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_camera_view_401_incorrect_password(self, mock_api_client_class, mock_messagebox):
        """Test load_camera_view with 401 incorrect password error."""
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
        mock_api_client.get_camera_view.side_effect = Exception("401: Incorrect password")
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1
        panel.camera_passwords[1] = "wrongpass"

        panel.load_camera_view(1, password="wrongpass")

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Incorrect password" in call_args[1]

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_adjust_zoom_no_camera(self, mock_api_client_class, mock_messagebox):
        """Test adjust_zoom with no camera selected."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = None

        panel.adjust_zoom(1)

        mock_api_client.control_camera_ptz.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_adjust_zoom_limit_reached(self, mock_api_client_class, mock_messagebox):
        """Test adjust_zoom with limit reached."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client.control_camera_ptz.return_value = {
            "success": False,
            "message": "Zoom limit reached",
            "zoom_level": 9,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1
        panel.current_zoom = 9

        panel.adjust_zoom(1)

        mock_messagebox.showwarning.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_reset_zoom_no_camera(self, mock_api_client_class, mock_messagebox):
        """Test reset_zoom with no camera selected."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = None

        panel.reset_zoom()

        mock_api_client.control_camera_ptz.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_adjust_pan_no_camera(self, mock_api_client_class, mock_messagebox):
        """Test adjust_pan with no camera selected."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = None

        panel.adjust_pan(1)

        mock_api_client.control_camera_ptz.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_adjust_pan_limit_reached(self, mock_api_client_class, mock_messagebox):
        """Test adjust_pan with limit reached."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client.control_camera_ptz.return_value = {
            "success": False,
            "message": "Pan limit reached",
            "pan_position": 5,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1
        panel.current_pan = 5

        panel.adjust_pan(1)

        mock_messagebox.showwarning.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_reset_pan_no_camera(self, mock_api_client_class, mock_messagebox):
        """Test reset_pan with no camera selected."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = None

        panel.reset_pan()

        mock_api_client.control_camera_ptz.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_disable_camera_no_selection(self, mock_api_client_class, mock_messagebox):
        """Test disabling camera with no selection."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.disable_camera()

        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_set_camera_password_no_selection(self, mock_api_client_class, mock_messagebox, mock_simpledialog):
        """Test set_camera_password with no selection."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.set_camera_password()

        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_set_camera_password_mismatch(self, mock_api_client_class, mock_messagebox, mock_simpledialog):
        """Test set_camera_password with password mismatch."""
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
        mock_simpledialog.askstring.side_effect = ["newpass123", "differentpass"]

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            break

        panel.set_camera_password()

        mock_messagebox.showerror.assert_called_once()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Passwords do not match" in call_args[1]

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_delete_camera_password_no_selection(self, mock_api_client_class, mock_messagebox, mock_simpledialog):
        """Test delete_camera_password with no selection."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.delete_camera_password()

        mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_delete_camera_password_no_password(self, mock_api_client_class, mock_messagebox, mock_simpledialog):
        """Test delete_camera_password when camera has no password."""
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

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            break

        panel.delete_camera_password()

        mock_messagebox.showinfo.assert_called_once()
        call_args = mock_messagebox.showinfo.call_args[0]
        assert "no password set" in call_args[1].lower()

        root.destroy()

    @patch("frontend.surveillance_panel.SensorPanel")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_open_sensor_panel(self, mock_api_client_class, mock_messagebox, mock_sensor_panel):
        """Test opening sensor panel."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {"cameras": []}
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"
        app.dashboard = Mock()
        app.dashboard.security_panel = Mock()
        app.dashboard.security_panel.load_intrusion_log = Mock()

        panel = SurveillancePanel(root, app)

        panel.open_sensor_panel()

        mock_sensor_panel.assert_called_once()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_select_camera_from_floor_plan(self, mock_api_client_class, mock_messagebox):
        """Test selecting camera from floor plan."""
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

        panel.select_camera_from_floor_plan(1)

        # Should select the camera in the tree
        selected = panel.camera_tree.selection()
        assert len(selected) > 0

        root.destroy()

    @patch("frontend.surveillance_panel.ImageTk")
    @patch("frontend.surveillance_panel.Image")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_show_floor_plan(self, mock_api_client_class, mock_messagebox, mock_image, mock_imagetk):
        """Test showing floor plan."""
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

        # Mock floor plan file
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.__truediv__", return_value=Path("floorplan.png")):
                panel.show_floor_plan()

        # Window should be created
        # (We can't easily verify the window content, but we can verify it doesn't error)

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_show_thumbnails_no_eligible(self, mock_api_client_class, mock_messagebox):
        """Test show_thumbnails with no eligible cameras."""
        mock_api_client = Mock()
        mock_api_client.list_cameras.return_value = {
            "cameras": [
                {
                    "camera_id": 1,
                    "name": "Camera 1",
                    "location": "Living Room",
                    "is_enabled": True,
                    "is_online": True,
                    "has_password": True,  # Has password, not eligible
                },
            ]
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.show_thumbnails()

        mock_messagebox.showinfo.assert_called_once()
        call_args = mock_messagebox.showinfo.call_args[0]
        assert "No Cameras" in call_args[0]

        root.destroy()

    @patch("frontend.surveillance_panel.ImageTk")
    @patch("frontend.surveillance_panel.Image")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_view_camera_from_thumbnail(self, mock_api_client_class, mock_messagebox, mock_image, mock_imagetk):
        """Test viewing camera from thumbnail."""
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

        mock_window = Mock()
        panel.view_camera_from_thumbnail(1, mock_window)

        # Should select the camera
        selected = panel.camera_tree.selection()
        assert len(selected) > 0

        root.destroy()

    @patch("frontend.surveillance_panel.ImageTk")
    @patch("frontend.surveillance_panel.Image")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_camera_view_with_image(
        self, mock_api_client_class, mock_messagebox, mock_image, mock_imagetk
    ):
        """Test load_camera_view with image loading."""
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
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 1,
            "zoom_level": 3,
            "image_url": "/path/to/camera1.jpg",
            "current_time": 12345,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1

        # Mock image file exists
        mock_img = Mock()
        mock_img.width = 640
        mock_img.height = 480
        mock_image.open.return_value = mock_img

        # Mock _generate_camera_view
        mock_view_img = Mock()
        mock_view_img.resize = Mock(return_value=mock_view_img)
        with patch.object(panel, "_generate_camera_view", return_value=mock_view_img):
            with patch("pathlib.Path.exists", return_value=True):
                panel.load_camera_view(1)

        mock_image.open.assert_called()
        mock_view_img.resize.assert_called()

        root.destroy()

    @patch("frontend.surveillance_panel.ImageTk")
    @patch("frontend.surveillance_panel.Image")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_camera_view_image_not_found(
        self, mock_api_client_class, mock_messagebox, mock_image, mock_imagetk
    ):
        """Test load_camera_view with image file not found."""
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
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 0,
            "zoom_level": 2,
            "image_url": "/path/to/nonexistent.jpg",
            "current_time": 0,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1

        with patch("pathlib.Path.exists", return_value=False):
            panel.load_camera_view(1)

        # Should show "Image not found" message on canvas
        # (We can't easily verify canvas content, but we can verify it doesn't error)

        root.destroy()

    @patch("frontend.surveillance_panel.ImageTk")
    @patch("frontend.surveillance_panel.Image")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_camera_view_image_load_error(
        self, mock_api_client_class, mock_messagebox, mock_image, mock_imagetk
    ):
        """Test load_camera_view with image load error."""
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
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 0,
            "zoom_level": 2,
            "image_url": "/path/to/camera1.jpg",
            "current_time": 0,
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1

        mock_image.open.side_effect = Exception("Image load error")

        with patch("pathlib.Path.exists", return_value=True):
            panel.load_camera_view(1)

        # Should handle error gracefully

        root.destroy()

    def test_generate_camera_view(self):
        """Test _generate_camera_view method."""
        from PIL import Image

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        with patch("frontend.surveillance_panel.APIClient") as mock_api:
            mock_api.return_value.list_cameras.return_value = {"cameras": []}
            panel = SurveillancePanel(root, app)

            # Create a test image
            source_img = Image.new("RGB", (400, 300), "blue")

            # Test with different pan/zoom values
            result = panel._generate_camera_view(source_img, pan=0, zoom=5)
            assert result is not None
            assert result.size == (500, 500)

            result = panel._generate_camera_view(source_img, pan=3, zoom=2)
            assert result is not None
            assert result.size == (500, 500)

            result = panel._generate_camera_view(source_img, pan=-2, zoom=8)
            assert result is not None
            assert result.size == (500, 500)

            # Test with None source image
            result = panel._generate_camera_view(None, pan=0, zoom=2)
            assert result is not None
            assert result.size == (500, 500)

        root.destroy()

    @patch("frontend.surveillance_panel.ImageTk")
    @patch("frontend.surveillance_panel.Image")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_show_thumbnails_success(
        self, mock_api_client_class, mock_messagebox, mock_image, mock_imagetk
    ):
        """Test show_thumbnails with successful thumbnail loading."""
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
        mock_api_client.get_camera_thumbnails.return_value = {
            "image_url": "/path/to/camera1.jpg",
            "captured_at": "2024-01-01 12:00:00",
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        mock_img = Mock()
        mock_img.thumbnail = Mock()
        mock_image.open.return_value = mock_img

        with patch("pathlib.Path.exists", return_value=True):
            panel.show_thumbnails()

        # Should create thumbnail window
        # (We can't easily verify window content, but we can verify it doesn't error)

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_show_thumbnails_connection_error(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test show_thumbnails with connection error."""
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
        mock_api_client.get_camera_thumbnails.side_effect = Exception(
            "Connection refused"
        )
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)

        panel.show_thumbnails()

        mock_messagebox.showerror.assert_called()
        call_args = mock_messagebox.showerror.call_args[0]
        assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_set_camera_password_cancel_old_password(
        self, mock_api_client_class, mock_messagebox, mock_simpledialog
    ):
        """Test set_camera_password when user cancels old password prompt."""
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
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        mock_simpledialog.askstring.return_value = None  # User cancels

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            break

        panel.set_camera_password()

        mock_api_client.set_camera_password.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_set_camera_password_cancel_new_password(
        self, mock_api_client_class, mock_messagebox, mock_simpledialog
    ):
        """Test set_camera_password when user cancels new password prompt."""
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
        mock_simpledialog.askstring.return_value = None  # User cancels

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            break

        panel.set_camera_password()

        mock_api_client.set_camera_password.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_delete_camera_password_cancel(
        self, mock_api_client_class, mock_messagebox, mock_simpledialog
    ):
        """Test delete_camera_password when user cancels."""
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
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        mock_simpledialog.askstring.return_value = None  # User cancels

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            break

        panel.delete_camera_password()

        mock_api_client.delete_camera_password.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.simpledialog")
    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_delete_camera_password_user_cancels_confirmation(
        self, mock_api_client_class, mock_messagebox, mock_simpledialog
    ):
        """Test delete_camera_password when user cancels confirmation."""
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
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        mock_simpledialog.askstring.return_value = "test123"
        mock_messagebox.askyesno.return_value = False  # User cancels

        for item in panel.camera_tree.get_children():
            panel.camera_tree.selection_set(item)
            break

        panel.delete_camera_password()

        mock_api_client.delete_camera_password.assert_not_called()

        root.destroy()

    @patch("frontend.surveillance_panel.messagebox")
    @patch("frontend.surveillance_panel.APIClient")
    def test_load_camera_view_no_image_url(
        self, mock_api_client_class, mock_messagebox
    ):
        """Test load_camera_view with no image_url in response."""
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
        mock_api_client.get_camera_view.return_value = {
            "pan_position": 0,
            "zoom_level": 2,
            "current_time": 0,
            # No image_url
        }
        mock_api_client_class.return_value = mock_api_client

        root = tk.Tk()
        root.withdraw()
        app = Mock()

        panel = SurveillancePanel(root, app)
        panel.current_camera = 1

        panel.load_camera_view(1)

        # Should still display camera info even without image

        root.destroy()
