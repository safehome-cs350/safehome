"""Tests for login window."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.login_window import LoginWindow


class TestLoginWindow:
    """Test cases for LoginWindow class."""

    def test_init(self):
        """Test LoginWindow initialization."""
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        assert window.on_success == callback
        assert window.title() == "SafeHome - Login"
        assert hasattr(window, "username_entry")
        assert hasattr(window, "password_entry")
        assert hasattr(window, "password2_entry")

        root.destroy()

    def test_center_window(self):
        """Test window centering."""
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
        """Test login with empty fields."""
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
        """Test login with invalid credentials."""
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        window.username_entry.insert(0, "wrong")
        window.password_entry.insert(0, "wrong")
        window.password2_entry.insert(0, "wrong")

        with patch.object(window.api_client, "login") as mock_login:
            mock_login.side_effect = Exception("401: Invalid credentials")
            window.handle_login()

            mock_messagebox.showerror.assert_called_once()
            callback.assert_not_called()

        root.destroy()

    @patch("frontend.login_window.messagebox")
    def test_handle_login_success(self, mock_messagebox):
        """Test successful login."""
        root = tk.Tk()
        root.withdraw()
        callback = Mock()
        window = LoginWindow(root, callback)

        window.username_entry.insert(0, "admin")
        window.password_entry.insert(0, "admin123")
        window.password2_entry.insert(0, "admin456")

        with patch.object(window.api_client, "login") as mock_login:
            mock_login.return_value = {"message": "Welcome!"}
            window.handle_login()

            mock_login.assert_called_once_with("admin", "admin123", "admin456")
            mock_messagebox.showerror.assert_not_called()
            callback.assert_called_once_with("admin")

        root.destroy()
