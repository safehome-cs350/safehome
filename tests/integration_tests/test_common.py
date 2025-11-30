"""Common integration tests."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from control_panel.control_panel import ControlPanel, ControlPanelState
from frontend.configuration_panel import ConfigurationPanel
from frontend.login_window import LoginWindow
from frontend.surveillance_panel import SurveillancePanel


@pytest.fixture
def tk_root():
    """Provide a Tk root window."""
    root = tk.Tk()
    yield root
    root.destroy()


def test_uc_1a():
    """Test for UC1.a. Log onto the system through control panel."""
    # 1. The homeowner/guest uses the control panel.
    control_panel = ControlPanel()

    # 2. The homeowner/guest enters master/guest password. (4 digits password)
    # 3. The system validates password.
    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()

    # 4. The system shows accessible functions on the control panel.
    assert control_panel.state == ControlPanelState.MASTER


def test_uc_1b(tk_root):
    """Test for UC1.b. Log onto the system through web browser."""
    # 1. The homeowner connects SafeHome web page.
    callback = Mock()
    login_window = LoginWindow(tk_root, callback)

    # 2. The homeowner enters user ID.
    login_window.username_entry.insert(0, "homeowner1")

    # 3. The homeowner enters two level passwords, each have 8 characters.
    login_window.password_entry.insert(0, "12345678")
    login_window.password2_entry.insert(0, "abcdefgh")

    # 4. The system validates the password.
    login_window.handle_login()

    # 5. The system displays all major function buttons and home safety status.
    callback.assert_called_once_with("homeowner1")


def test_uc_1c(tk_root):
    """Test for UC1.c. Configure system setting."""
    # 1, 2
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    config_panel = ConfigurationPanel(tk_root, mock_app)

    # 3, 4
    config_panel.phone_number_var.set("010-9876-5432")

    # 5
    with patch("tkinter.messagebox.showinfo") as mock_showinfo:
        config_panel.save_settings()

    # 6
    mock_showinfo.assert_called_once_with("Success", "Settings saved successfully")


def test_uc_1d():
    """Test for UC1.d. Turn the system on."""
    control_panel = ControlPanel()

    # Login
    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.MASTER

    # Power off
    control_panel.button2()
    assert control_panel.state == ControlPanelState.POWERED_OFF

    # Power on
    control_panel.button1()
    assert control_panel.state == ControlPanelState.IDLE


def test_uc_1e():
    """Test for UC1.e. Turn the system off."""
    control_panel = ControlPanel()

    # Login
    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.MASTER

    # Power off
    control_panel.button2()
    assert control_panel.state == ControlPanelState.POWERED_OFF


def test_uc_1f():
    """Test for UC1.f. Reset the system."""
    control_panel = ControlPanel()

    # Login
    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.MASTER

    # Reset
    control_panel.button3()
    assert control_panel.state == ControlPanelState.IDLE


def test_uc_1g():
    """Test for UC1.g. Change master password through control panel."""
    control_panel = ControlPanel()

    # Login
    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.MASTER

    # Change password
    control_panel.button6()
    assert control_panel.state == ControlPanelState.PASSWORD_CHANGE_CURRENT

    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.PASSWORD_CHANGE_NEW

    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.PASSWORD_CHANGE_RECONFIRM

    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.MASTER


def test_uc_2a():
    """Test for UC2.a. Arm/disarm system through control panel."""
    control_panel = ControlPanel()

    control_panel.button1()
    control_panel.button2()
    control_panel.button3()
    control_panel.button4()
    assert control_panel.state == ControlPanelState.MASTER

    with patch.object(control_panel, "set_armed_led") as mock_armed_led:
        control_panel.button4()
        mock_armed_led.assert_called_once_with(True)

    with patch.object(control_panel, "set_armed_led") as mock_armed_led:
        control_panel.button5()
        mock_armed_led.assert_called_once_with(False)


def test_uc_3a(tk_root):
    """Test for UC3.a. Display Specific camera view."""
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
