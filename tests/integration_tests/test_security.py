"""Security integration tests."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from control_panel.control_panel import ControlPanel, ControlPanelState
from frontend.security_panel import SecurityPanel


@pytest.fixture
def tk_root():
    """Provide a Tk root window."""
    root = tk.Tk()
    yield root
    root.destroy()


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


def test_uc_2b(tk_root):
    """Test for UC2.b. Arm/disarm system through web browser."""
    control_panel = ControlPanel()

    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    security_panel = SecurityPanel(tk_root, mock_app)

    # Away
    security_panel.mode_var.set("away")
    with (
        patch("tkinter.messagebox.askyesno", return_value=True),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.arm_system()

    mock_showinfo.assert_called_once_with("Success", "System armed successfully")

    control_panel.poll_alarm()
    assert control_panel.armed is True

    # Stay
    security_panel.mode_var.set("home")
    with (
        patch("tkinter.messagebox.askyesno", return_value=True),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.arm_system()

    mock_showinfo.assert_called_once_with("Success", "System armed successfully")

    control_panel.poll_alarm()
    assert control_panel.armed is False
