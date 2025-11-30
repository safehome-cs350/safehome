"""Common integration tests."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from control_panel.control_panel import ControlPanel, ControlPanelState
from frontend.configuration_panel import ConfigurationPanel
from frontend.login_window import LoginWindow


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
