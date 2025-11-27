"""Tests for login window."""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from frontend.login_window import LoginWindow


class TestLoginWindow:
    """Test cases for LoginWindow class."""

    def test_init(self):
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        assert window.on_success == callback
        assert window.default_username == "admin"
        assert window.default_password == "admin123"
        assert window.title() == "SafeHome - Login"

        root.destroy()

    def test_center_window(self):
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        window.center_window()
        geometry = window.geometry()
        assert "x" in geometry
        assert "+" in geometry

        root.destroy()

    @patch("frontend.login_window.messagebox")
    def test_handle_login_empty_fields(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        window.handle_login()

        mock_messagebox.showerror.assert_called_once()
        callback.assert_not_called()

        root.destroy()

    @patch("frontend.login_window.messagebox")
    def test_handle_login_invalid_credentials(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        window.username_entry.insert(0, "wrong")
        window.password_entry.insert(0, "wrong")

        window.handle_login()

        mock_messagebox.showerror.assert_called_once()
        callback.assert_not_called()

        root.destroy()

    @patch("frontend.login_window.messagebox")
    def test_handle_login_success(self, mock_messagebox):
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        window.username_entry.insert(0, "admin")
        window.password_entry.insert(0, "admin123")

        window.handle_login()

        mock_messagebox.showerror.assert_not_called()
        callback.assert_called_once_with("admin")

        root.destroy()
