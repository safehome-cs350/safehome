"""Common integration tests."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from frontend.configuration_panel import ConfigurationPanel
from frontend.login_window import LoginWindow


@pytest.fixture
def tk_root():
    """Provide a Tk root window."""
    root = tk.Tk()
    yield root
    root.destroy()


def test_uc_1b(tk_root):
    """Test for UC1.b. Log onto the system through web browser."""
    # 1. The homeowner connects SafeHome web page.
    callback = Mock()
    login_window = LoginWindow(tk_root, callback)

    # 2. The homeowner enters user ID.
    login_window.username_entry.insert(0, "admin")

    # 3. The homeowner enters two level passwords, each have 8 characters.
    login_window.password_entry.insert(0, "admin123")

    # 4. The system validates the password.
    login_window.handle_login()

    # 5. The system displays all major function buttons and home safety status.
    callback.assert_called_once_with("admin")


def test_uc_1c(tk_root):
    """Test for UC1.c. Configure system setting."""
    # 1, 2
    mock_app = Mock()
    config_panel = ConfigurationPanel(tk_root, mock_app)

    # 3, 4
    config_panel.delay_time_var.set("100")
    config_panel.phone_number_var.set("010-9876-5432")

    # 5
    with patch("tkinter.messagebox.showinfo") as mock_showinfo:
        config_panel.save_settings()

    # 6
    mock_showinfo.assert_called_once_with("Success", "Settings saved successfully")
