"""Tests for main application."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.main import SafeHomeApp


class TestSafeHomeApp:
    """Test cases for SafeHomeApp class."""

    def test_init(self):
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow") as mock_login:
            app = SafeHomeApp()

            assert not app.is_logged_in
            assert app.current_user is None
            assert app.dashboard is None
            mock_login.assert_called_once()

            app.root.destroy()

    def test_on_login_success(self):
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow"):
            app = SafeHomeApp()

            with patch("frontend.main.MainDashboard") as mock_dashboard:
                app.on_login_success("test_user")

                assert app.is_logged_in
                assert app.current_user == "test_user"
                mock_dashboard.assert_called_once()

            app.root.destroy()

    def test_logout(self):
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow") as mock_login:
            app = SafeHomeApp()
            app.is_logged_in = True
            app.current_user = "test_user"

            app.logout()

            assert not app.is_logged_in
            assert app.current_user is None
            assert app.dashboard is None
            mock_login.assert_called()

            app.root.destroy()

    def test_update_status(self):
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow"):
            app = SafeHomeApp()

            with patch("frontend.main.MainDashboard") as mock_dashboard_class:
                mock_dashboard = Mock()
                mock_dashboard.update_status = Mock()
                mock_dashboard_class.return_value = mock_dashboard

                app.on_login_success("test_user")
                app.update_status("Test message")

                mock_dashboard.update_status.assert_called_once_with("Test message")

            app.root.destroy()

    def test_update_status_no_dashboard(self):
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow"):
            app = SafeHomeApp()
            app.dashboard = None

            app.update_status("Test message")

            assert True

            app.root.destroy()
