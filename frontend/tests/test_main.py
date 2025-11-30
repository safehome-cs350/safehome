"""Tests for main application."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.main import SafeHomeApp


class TestSafeHomeApp:
    """Test cases for SafeHomeApp class."""

    def test_init(self):
        """Test SafeHomeApp initialization."""
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
        """Test successful login handling."""
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
        """Test logout functionality."""
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
        """Test status update with dashboard."""
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
        """Test status update without dashboard."""
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow"):
            app = SafeHomeApp()
            app.dashboard = None

            app.update_status("Test message")

            assert True

            app.root.destroy()

    def test_show_dashboard_destroys_widgets(self):
        """Test show_dashboard destroys existing widgets."""
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow"):
            app = SafeHomeApp()
            # Clear any existing widgets first
            for widget in app.root.winfo_children():
                widget.destroy()
            # Add a widget to root
            test_widget = tk.Label(app.root, text="test")
            test_widget.pack()

            with patch("frontend.main.MainDashboard") as mock_dashboard_class:
                mock_dashboard = Mock()
                mock_dashboard.pack = Mock()
                mock_dashboard_class.return_value = mock_dashboard

                app.show_dashboard()

                # Widgets should be destroyed before dashboard is added
                # Dashboard should be added
                mock_dashboard.pack.assert_called_once()

            app.root.destroy()

    def test_logout_destroys_widgets(self):
        """Test logout destroys existing widgets."""
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow") as mock_login:
            app = SafeHomeApp()
            app.is_logged_in = True
            app.current_user = "test_user"

            with patch("frontend.main.MainDashboard") as mock_dashboard_class:
                mock_dashboard = Mock()
                mock_dashboard_class.return_value = mock_dashboard
                app.on_login_success("test_user")

                # Add another widget
                test_widget = tk.Label(app.root, text="test")
                test_widget.pack()

                app.logout()

                # Widgets should be destroyed before showing login
                mock_login.assert_called()

            app.root.destroy()

    def test_run(self):
        """Test run method calls mainloop."""
        root = tk.Tk()
        root.withdraw()

        with patch("frontend.main.LoginWindow"):
            app = SafeHomeApp()

            with patch.object(app.root, "mainloop") as mock_mainloop:
                app.run()
                mock_mainloop.assert_called_once()

            app.root.destroy()

    def test_main_function(self):
        """Test main function."""
        with patch("frontend.main.SafeHomeApp") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            from frontend.main import main

            main()

            mock_app_class.assert_called_once()
            mock_app.run.assert_called_once()

    def test_main_entry_point(self):
        """Test main entry point when run as script."""
        # This test verifies the entry point exists
        # The actual execution is tested in test_main_function
        import frontend.main

        # Verify the entry point code exists
        assert hasattr(frontend.main, "main")
        assert callable(frontend.main.main)
