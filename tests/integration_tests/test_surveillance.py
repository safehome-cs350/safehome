"""Surveillance integration tests."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from frontend.surveillance_panel import SurveillancePanel


@pytest.fixture
def tk_root():
    """Provide a Tk root window."""
    root = tk.Tk()
    yield root
    root.destroy()


def test_uc_3a(tk_root):
    """Test for UC3.a. Display Specific camera view."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    panel = SurveillancePanel(tk_root, mock_app)

    item = panel.camera_tree.get_children()[0]
    panel.camera_tree.selection_set(item)

    with patch("tkinter.Canvas.create_image") as mock_create_image:
        panel.on_camera_select(None)

    mock_create_image.assert_called_once()


def test_uc_3b(tk_root):
    """Test for UC3.b. Pan/Zoom specific camera view."""
    pass


def test_uc_3c(tk_root):
    """Test for UC3.c. Set camera password."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    panel = SurveillancePanel(tk_root, mock_app)

    item = panel.camera_tree.get_children()[0]
    panel.camera_tree.selection_set(item)

    with (
        patch("tkinter.simpledialog.askstring", return_value="1234"),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        panel.set_camera_password()

    mock_showinfo.assert_called_once_with("Success", "Camera password set")


def test_uc_3d(tk_root):
    """Test for UC3.d. Delete camera password."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    panel = SurveillancePanel(tk_root, mock_app)

    item = panel.camera_tree.get_children()[1]
    panel.camera_tree.selection_set(item)

    with (
        patch("tkinter.simpledialog.askstring", return_value="camera123"),
        patch("tkinter.messagebox.askyesno", return_value=True),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        panel.delete_camera_password()

    mock_showinfo.assert_called_once_with("Success", "Camera password deleted")


def test_uc_3e(tk_root):
    """Test for UC3.e. View thumbnail Shots."""
    pass


def test_uc_3f(tk_root):
    """Test for UC3.f. Enable camera."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    panel = SurveillancePanel(tk_root, mock_app)

    item = panel.camera_tree.get_children()[2]
    panel.camera_tree.selection_set(item)

    with patch("tkinter.messagebox.showinfo") as mock_showinfo:
        panel.enable_camera()

    mock_showinfo.assert_called_once_with("Success", "Camera enabled")


def test_uc_3g(tk_root):
    """Test for UC3.g. Disable camera."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    panel = SurveillancePanel(tk_root, mock_app)

    item = panel.camera_tree.get_children()[0]
    panel.camera_tree.selection_set(item)

    with patch("tkinter.messagebox.showinfo") as mock_showinfo:
        panel.disable_camera()

    mock_showinfo.assert_called_once_with("Success", "Camera disabled")
