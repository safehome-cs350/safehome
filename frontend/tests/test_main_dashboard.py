import tkinter as tk
from unittest.mock import Mock

import pytest

from frontend.main_dashboard import MainDashboard


class TestMainDashboard:
    def test_init(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"

        dashboard = MainDashboard(root, app)

        assert dashboard.app == app
        assert hasattr(dashboard, "content_notebook")
        assert hasattr(dashboard, "status_label")

        root.destroy()

    def test_show_panel(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"

        dashboard = MainDashboard(root, app)

        dashboard.show_panel("security")
        assert dashboard.content_notebook.index(dashboard.content_notebook.select()) == 0

        dashboard.show_panel("surveillance")
        assert dashboard.content_notebook.index(dashboard.content_notebook.select()) == 1

        dashboard.show_panel("configuration")
        assert dashboard.content_notebook.index(dashboard.content_notebook.select()) == 2

        root.destroy()

    def test_update_status(self):
        root = tk.Tk()
        root.withdraw()
        app = Mock()
        app.current_user = "test_user"

        dashboard = MainDashboard(root, app)

        dashboard.update_status("Test status")
        assert dashboard.status_label.cget("text") == "Test status"

        root.destroy()
