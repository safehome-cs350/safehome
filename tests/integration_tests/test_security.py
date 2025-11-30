"""Security integration tests."""

import tkinter as tk
from unittest.mock import MagicMock, Mock, patch

import pytest

from control_panel.control_panel import ControlPanel, ControlPanelState
from frontend.security_panel import SafetyZoneDialog, SecurityPanel


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


def test_uc_2c(tk_root):
    """Test for UC2.c. Arm/disarm safety zone selectively."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    security_panel = SecurityPanel(tk_root, mock_app)

    zone_name = "Zone1"

    original_init = SafetyZoneDialog.__init__

    # Create
    def mock_init(self, parent, zone_data, available_devices):
        original_init(self, parent, zone_data, available_devices)
        self.name_entry.insert(0, zone_name)
        self.device_listbox.selection_set(0)
        self.ok_clicked()

    with (
        patch.object(SafetyZoneDialog, "__init__", mock_init),
        patch.object(security_panel, "wait_window", MagicMock(return_value=None)),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.create_zone()

    mock_showinfo.assert_called_once_with(
        "Success", f"Zone '{zone_name}' created successfully"
    )

    # Select the created zone
    item = security_panel.zones_tree.get_children()[0]
    security_panel.zones_tree.selection_set(item)

    # Arm the zone
    with patch("tkinter.messagebox.showinfo") as mock_showinfo:
        security_panel.toggle_zone()

    mock_showinfo.assert_called_once_with("Success", f"Zone '{zone_name}' armed")

    # Disarm the zone
    item = security_panel.zones_tree.get_children()[0]
    security_panel.zones_tree.selection_set(item)

    with patch("tkinter.messagebox.showinfo") as mock_showinfo:
        security_panel.toggle_zone()

    mock_showinfo.assert_called_once_with("Success", f"Zone '{zone_name}' disarmed")

    # Delete
    item = security_panel.zones_tree.get_children()[0]
    security_panel.zones_tree.selection_set(item)

    with (
        patch("tkinter.messagebox.askyesno", return_value=True),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.delete_zone()

    mock_showinfo.assert_called_once_with(
        "Success", f"Zone '{zone_name}' deleted successfully"
    )


def test_uc_2d(tk_root):
    """Test for UC2.d. Alarm condition encountered."""
    pass


def test_uc_2e(tk_root):
    """Test for UC2.e. Configure safety zone."""
    pass


def test_uc_2f_2g(tk_root):
    """Test for UC2.f. Create new safety zone and UC2.g. Delete safety zone."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    security_panel = SecurityPanel(tk_root, mock_app)

    zone_name = "Zone1"

    original_init = SafetyZoneDialog.__init__

    # Create
    def mock_init(self, parent, zone_data, available_devices):
        original_init(self, parent, zone_data, available_devices)
        self.name_entry.insert(0, zone_name)
        self.device_listbox.selection_set(0)
        self.ok_clicked()

    with (
        patch.object(SafetyZoneDialog, "__init__", mock_init),
        patch.object(security_panel, "wait_window", MagicMock(return_value=None)),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.create_zone()

    mock_showinfo.assert_called_once_with(
        "Success", f"Zone '{zone_name}' created successfully"
    )

    item = security_panel.zones_tree.get_children()[0]
    security_panel.zones_tree.selection_set(item)

    # Delete
    with (
        patch("tkinter.messagebox.askyesno", return_value=True),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.delete_zone()

    mock_showinfo.assert_called_once_with(
        "Success", f"Zone '{zone_name}' deleted successfully"
    )


def test_uc_2h(tk_root):
    """Test for UC2.h. Update an exist safety zone."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    security_panel = SecurityPanel(tk_root, mock_app)

    zone_name = "Zone1"

    original_init = SafetyZoneDialog.__init__

    # Create
    def mock_init_create(self, parent, zone_data, available_devices):
        original_init(self, parent, zone_data, available_devices)
        self.name_entry.insert(0, zone_name)
        self.device_listbox.selection_set(0)
        self.ok_clicked()

    with (
        patch.object(SafetyZoneDialog, "__init__", mock_init_create),
        patch.object(security_panel, "wait_window", MagicMock(return_value=None)),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.create_zone()

    mock_showinfo.assert_called_once_with(
        "Success", f"Zone '{zone_name}' created successfully"
    )

    # Update
    item = security_panel.zones_tree.get_children()[0]
    security_panel.zones_tree.selection_set(item)

    def mock_init_update(self, parent, zone_data, available_devices):
        original_init(self, parent, zone_data, available_devices)
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, zone_name)
        self.device_listbox.selection_clear(0, tk.END)
        self.device_listbox.selection_set(1)
        self.ok_clicked()

    with (
        patch.object(SafetyZoneDialog, "__init__", mock_init_update),
        patch.object(security_panel, "wait_window", MagicMock(return_value=None)),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.edit_zone()

    mock_showinfo.assert_called_once_with(
        "Success", f"Zone '{zone_name}' updated successfully"
    )

    # Delete
    item = security_panel.zones_tree.get_children()[0]
    security_panel.zones_tree.selection_set(item)

    with (
        patch("tkinter.messagebox.askyesno", return_value=True),
        patch("tkinter.messagebox.showinfo") as mock_showinfo,
    ):
        security_panel.delete_zone()

    mock_showinfo.assert_called_once_with(
        "Success", f"Zone '{zone_name}' deleted successfully"
    )


def test_uc_2i(tk_root):
    """Test for UC2.i. Configure SafeHome modes."""
    mock_app = Mock()
    mock_app.current_user = "homeowner1"
    security_panel = SecurityPanel(tk_root, mock_app)

    # Test changing to "away" mode
    with patch("tkinter.messagebox.showinfo"):
        security_panel.mode_var.set("away")
        tk_root.update()

    assert security_panel.current_mode == "away"

    # Test changing to "home" mode
    with patch("tkinter.messagebox.showinfo"):
        security_panel.mode_var.set("home")
        tk_root.update()

    assert security_panel.current_mode == "home"
