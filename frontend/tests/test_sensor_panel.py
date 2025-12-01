"""Tests for sensor panel."""

import tkinter as tk
from unittest.mock import Mock, patch

from frontend.sensor_panel import SensorPanel


class TestSensorPanel:
    """Test cases for SensorPanel class."""

    def test_init(self):
        """Test SensorPanel initialization."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, user_id="user1", log_refresh_callback=Mock())

            assert panel.user_id == "user1"
            assert panel.log_refresh_callback is not None
            assert panel.title() == "Sensor Test"
            assert hasattr(panel, "windoor_id_var")
            assert hasattr(panel, "motion_id_var")

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_load_sensors_success(self, mock_messagebox):
        """Test successful load sensors."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors", lambda x: None):
            panel = SensorPanel(root)

        with patch.object(panel.api_client, "list_sensors") as mock_list:
            mock_list.return_value = {
                "sensors": [
                    {"sensor_id": 1, "sensor_type": "motion", "is_armed": False},
                    {"sensor_id": 2, "sensor_type": "windoor", "is_armed": False},
                ]
            }
            with patch.object(panel, "refresh_status") as mock_refresh:
                panel.load_sensors()

                mock_list.assert_called_once()
                mock_refresh.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_load_sensors_connection_error(self, mock_messagebox):
        """Test load sensors with connection error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors", lambda x: None):
            panel = SensorPanel(root)

        with patch.object(panel.api_client, "list_sensors") as mock_list:
            mock_list.side_effect = Exception("Connection refused")
            panel.load_sensors()

            mock_messagebox.showerror.assert_called_once()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "Cannot connect to backend server" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_load_sensors_generic_error(self, mock_messagebox):
        """Test load sensors with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors", lambda x: None):
            panel = SensorPanel(root)

        with patch.object(panel.api_client, "list_sensors") as mock_list:
            mock_list.side_effect = Exception("Some error")
            panel.load_sensors()

            mock_messagebox.showerror.assert_called_once()
            call_args = mock_messagebox.showerror.call_args[0]
            assert "Failed to load sensors" in call_args[1]

        root.destroy()

    def test_refresh_status(self):
        """Test refresh status."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.sensors = {
                ("windoor", 1): {
                    "is_armed": True,
                    "is_triggered": False,
                    "location": "Test Location",
                },
                ("motion", 1): {
                    "is_armed": False,
                    "is_triggered": True,
                    "location": "Test Location",
                },
            }
            panel.windoor_sensor_ids = [1]
            panel.motion_sensor_ids = [1]

            panel.refresh_status()

            # Check windoor tree has items
            windoor_items = panel.windoor_tree.get_children()
            assert len(windoor_items) == 1
            windoor_values = panel.windoor_tree.item(windoor_items[0], "values")
            assert windoor_values[0] == "1"  # sensor_id
            assert windoor_values[2] == "Armed"  # armed status
            assert windoor_values[3] == "CLOSED"  # door status

            # Check motion tree has items
            motion_items = panel.motion_tree.get_children()
            assert len(motion_items) == 1
            motion_values = panel.motion_tree.item(motion_items[0], "values")
            assert motion_values[0] == "1"  # sensor_id
            assert motion_values[2] == "Disarmed"  # armed status
            assert motion_values[3] == "DETECTED"  # motion status

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_get_windoor_id_valid(self, mock_messagebox):
        """Test get windoor ID with valid ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1, 2, 3]
            panel.windoor_id_var.set("2")

            result = panel.get_windoor_id()
            assert result == 2
            mock_messagebox.showerror.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_get_windoor_id_invalid_range(self, mock_messagebox):
        """Test get windoor ID with invalid range."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1, 2, 3]
            panel.windoor_id_var.set("5")

            result = panel.get_windoor_id()
            assert result is None
            mock_messagebox.showerror.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_get_windoor_id_invalid_value(self, mock_messagebox):
        """Test get windoor ID with invalid value."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1, 2, 3]
            panel.windoor_id_var.set("invalid")

            result = panel.get_windoor_id()
            assert result is None
            mock_messagebox.showerror.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_get_motion_id_valid(self, mock_messagebox):
        """Test get motion ID with valid ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1, 2, 3]
            panel.motion_id_var.set("2")

            result = panel.get_motion_id()
            assert result == 2
            mock_messagebox.showerror.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_get_motion_id_invalid_range(self, mock_messagebox):
        """Test get motion ID with invalid range."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1, 2, 3]
            panel.motion_id_var.set("5")

            result = panel.get_motion_id()
            assert result is None
            mock_messagebox.showerror.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_get_motion_id_invalid_value(self, mock_messagebox):
        """Test get motion ID with invalid value."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1, 2, 3]
            panel.motion_id_var.set("invalid")

            result = panel.get_motion_id()
            assert result is None
            mock_messagebox.showerror.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_windoor_success(self, mock_messagebox):
        """Test successful arm windoor."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "arm_windoor_sensor") as mock_arm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.arm_windoor()

                    mock_arm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_windoor_404_error(self, mock_messagebox):
        """Test arm windoor with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "arm_windoor_sensor") as mock_arm:
                mock_arm.side_effect = Exception("404: Sensor not found")
                panel.arm_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_windoor_success(self, mock_messagebox):
        """Test successful disarm windoor."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "disarm_windoor_sensor") as mock_disarm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.disarm_windoor()

                    mock_disarm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_open_windoor_success(self, mock_messagebox):
        """Test successful open windoor."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "open_windoor_sensor") as mock_open:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.open_windoor()

                    mock_open.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_close_windoor_success(self, mock_messagebox):
        """Test successful close windoor."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "close_windoor_sensor") as mock_close:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.close_windoor()

                    mock_close.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_motion_success(self, mock_messagebox):
        """Test successful arm motion."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "arm_motion_sensor") as mock_arm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.arm_motion()

                    mock_arm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_motion_success(self, mock_messagebox):
        """Test successful disarm motion."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "disarm_motion_sensor") as mock_disarm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.disarm_motion()

                    mock_disarm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_trigger_motion_success(self, mock_messagebox):
        """Test successful trigger motion."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "trigger_motion_sensor"
            ) as mock_trigger:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.trigger_motion()

                    mock_trigger.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_release_motion_success(self, mock_messagebox):
        """Test successful release motion."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root, log_refresh_callback=Mock())
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "release_motion_sensor"
            ) as mock_release:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.release_motion()

                    mock_release.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    mock_messagebox.showinfo.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_windoor_log_refresh_error(self, mock_messagebox):
        """Test arm windoor with log refresh error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "arm_windoor_sensor") as mock_arm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.arm_windoor()

                    mock_arm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    # Should not raise exception even if callback fails

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_windoor_none_id(self, mock_messagebox):
        """Test arm windoor with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("5")  # Invalid ID

            with patch.object(panel, "get_windoor_id", return_value=None):
                panel.arm_windoor()

                # Should return early without calling API
                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_windoor_none_id(self, mock_messagebox):
        """Test disarm windoor with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]

            with patch.object(panel, "get_windoor_id", return_value=None):
                panel.disarm_windoor()

                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_open_windoor_none_id(self, mock_messagebox):
        """Test open windoor with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]

            with patch.object(panel, "get_windoor_id", return_value=None):
                panel.open_windoor()

                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_close_windoor_none_id(self, mock_messagebox):
        """Test close windoor with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]

            with patch.object(panel, "get_windoor_id", return_value=None):
                panel.close_windoor()

                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_motion_none_id(self, mock_messagebox):
        """Test arm motion with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]

            with patch.object(panel, "get_motion_id", return_value=None):
                panel.arm_motion()

                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_motion_none_id(self, mock_messagebox):
        """Test disarm motion with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]

            with patch.object(panel, "get_motion_id", return_value=None):
                panel.disarm_motion()

                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_trigger_motion_none_id(self, mock_messagebox):
        """Test trigger motion with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]

            with patch.object(panel, "get_motion_id", return_value=None):
                panel.trigger_motion()

                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_release_motion_none_id(self, mock_messagebox):
        """Test release motion with None sensor ID."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]

            with patch.object(panel, "get_motion_id", return_value=None):
                panel.release_motion()

                mock_messagebox.showinfo.assert_not_called()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_windoor_generic_error(self, mock_messagebox):
        """Test arm windoor with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "arm_windoor_sensor") as mock_arm:
                mock_arm.side_effect = Exception("Generic error")
                panel.arm_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to arm sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_windoor_generic_error(self, mock_messagebox):
        """Test disarm windoor with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "disarm_windoor_sensor") as mock_disarm:
                mock_disarm.side_effect = Exception("Generic error")
                panel.disarm_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to disarm sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_open_windoor_generic_error(self, mock_messagebox):
        """Test open windoor with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "open_windoor_sensor") as mock_open:
                mock_open.side_effect = Exception("Generic error")
                panel.open_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to open sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_close_windoor_generic_error(self, mock_messagebox):
        """Test close windoor with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "close_windoor_sensor") as mock_close:
                mock_close.side_effect = Exception("Generic error")
                panel.close_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to close sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_motion_generic_error(self, mock_messagebox):
        """Test arm motion with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "arm_motion_sensor") as mock_arm:
                mock_arm.side_effect = Exception("Generic error")
                panel.arm_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to arm sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_motion_generic_error(self, mock_messagebox):
        """Test disarm motion with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "disarm_motion_sensor") as mock_disarm:
                mock_disarm.side_effect = Exception("Generic error")
                panel.disarm_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to disarm sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_trigger_motion_generic_error(self, mock_messagebox):
        """Test trigger motion with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "trigger_motion_sensor"
            ) as mock_trigger:
                mock_trigger.side_effect = Exception("Generic error")
                panel.trigger_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to trigger sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_release_motion_generic_error(self, mock_messagebox):
        """Test release motion with generic error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "release_motion_sensor"
            ) as mock_release:
                mock_release.side_effect = Exception("Generic error")
                panel.release_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Failed to release sensor" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_windoor_callback_exception(self, mock_messagebox):
        """Test arm windoor with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "arm_windoor_sensor") as mock_arm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.arm_windoor()

                    mock_arm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()
                    # Should not raise exception even if callback fails

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_windoor_callback_exception(self, mock_messagebox):
        """Test disarm windoor with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "disarm_windoor_sensor") as mock_disarm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.disarm_windoor()

                    mock_disarm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_open_windoor_callback_exception(self, mock_messagebox):
        """Test open windoor with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "open_windoor_sensor") as mock_open:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.open_windoor()

                    mock_open.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_close_windoor_callback_exception(self, mock_messagebox):
        """Test close windoor with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "close_windoor_sensor") as mock_close:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.close_windoor()

                    mock_close.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_motion_callback_exception(self, mock_messagebox):
        """Test arm motion with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "arm_motion_sensor") as mock_arm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.arm_motion()

                    mock_arm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_motion_callback_exception(self, mock_messagebox):
        """Test disarm motion with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "disarm_motion_sensor") as mock_disarm:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.disarm_motion()

                    mock_disarm.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_trigger_motion_callback_exception(self, mock_messagebox):
        """Test trigger motion with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "trigger_motion_sensor"
            ) as mock_trigger:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.trigger_motion()

                    mock_trigger.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_release_motion_callback_exception(self, mock_messagebox):
        """Test release motion with callback exception."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            callback = Mock(side_effect=Exception("Callback error"))
            panel = SensorPanel(root, log_refresh_callback=callback)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "release_motion_sensor"
            ) as mock_release:
                with patch.object(panel, "load_sensors") as mock_load:
                    panel.release_motion()

                    mock_release.assert_called_once_with(1)
                    mock_load.assert_called_once()
                    callback.assert_called_once()

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_windoor_404_error(self, mock_messagebox):
        """Test disarm windoor with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "disarm_windoor_sensor") as mock_disarm:
                mock_disarm.side_effect = Exception("404: Sensor not found")
                panel.disarm_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_open_windoor_404_error(self, mock_messagebox):
        """Test open windoor with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "open_windoor_sensor") as mock_open:
                mock_open.side_effect = Exception("404: Sensor not found")
                panel.open_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_close_windoor_404_error(self, mock_messagebox):
        """Test close windoor with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.windoor_sensor_ids = [1]
            panel.windoor_id_var.set("1")

            with patch.object(panel.api_client, "close_windoor_sensor") as mock_close:
                mock_close.side_effect = Exception("404: Sensor not found")
                panel.close_windoor()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_arm_motion_404_error(self, mock_messagebox):
        """Test arm motion with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "arm_motion_sensor") as mock_arm:
                mock_arm.side_effect = Exception("404: Sensor not found")
                panel.arm_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_disarm_motion_404_error(self, mock_messagebox):
        """Test disarm motion with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(panel.api_client, "disarm_motion_sensor") as mock_disarm:
                mock_disarm.side_effect = Exception("404: Sensor not found")
                panel.disarm_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_trigger_motion_404_error(self, mock_messagebox):
        """Test trigger motion with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "trigger_motion_sensor"
            ) as mock_trigger:
                mock_trigger.side_effect = Exception("404: Sensor not found")
                panel.trigger_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()

    @patch("frontend.sensor_panel.messagebox")
    def test_release_motion_404_error(self, mock_messagebox):
        """Test release motion with 404 error."""
        root = tk.Tk()
        root.withdraw()

        with patch.object(SensorPanel, "load_sensors"):
            panel = SensorPanel(root)
            panel.motion_sensor_ids = [1]
            panel.motion_id_var.set("1")

            with patch.object(
                panel.api_client, "release_motion_sensor"
            ) as mock_release:
                mock_release.side_effect = Exception("404: Sensor not found")
                panel.release_motion()

                mock_messagebox.showerror.assert_called_once()
                call_args = mock_messagebox.showerror.call_args[0]
                assert "Sensor not found" in call_args[1]

        root.destroy()
