"""Tests for surveillance API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from frontend.surveillance_api_client import SurveillanceAPIClient


class TestSurveillanceAPIClient:
    """Test cases for SurveillanceAPIClient class."""

    def test_init(self):
        """Test SurveillanceAPIClient initialization."""
        client = SurveillanceAPIClient()
        assert client.base_url == "http://localhost:8000"

        client = SurveillanceAPIClient("http://example.com")
        assert client.base_url == "http://example.com"

        client = SurveillanceAPIClient("http://example.com/")
        assert client.base_url == "http://example.com"

    @patch("frontend.surveillance_api_client.requests.get")
    def test_list_cameras_success(self, mock_get):
        """Test successful list cameras."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cameras": []}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.list_cameras()

        assert result == {"cameras": []}
        mock_get.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.get")
    def test_list_cameras_error(self, mock_get):
        """Test list cameras with error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Server error"}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.list_cameras()

        assert "500" in str(exc_info.value)
        assert "Server error" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_list_cameras_error_no_detail(self, mock_get):
        """Test list cameras with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.list_cameras()

        assert "500" in str(exc_info.value)
        assert "Failed to list cameras" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_camera_view_success(self, mock_get):
        """Test successful get camera view."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"camera_id": 1, "image_url": "url"}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.get_camera_view(1, "password123")

        assert result == {"camera_id": 1, "image_url": "url"}
        mock_get.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_camera_view_no_password(self, mock_get):
        """Test get camera view without password."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"camera_id": 1, "image_url": "url"}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.get_camera_view(1)

        assert result == {"camera_id": 1, "image_url": "url"}
        mock_get.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_camera_view_error(self, mock_get):
        """Test get camera view with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Unauthorized"}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_camera_view(1)

        assert "401" in str(exc_info.value)
        assert "Unauthorized" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_camera_view_error_no_detail(self, mock_get):
        """Test get camera view with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_camera_view(1)

        assert "500" in str(exc_info.value)
        assert "Failed to get camera view" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_control_camera_ptz_success(self, mock_post):
        """Test successful control camera PTZ."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"pan_position": 2, "zoom_level": 5}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.control_camera_ptz(1, pan=2, zoom=5)

        assert result == {"pan_position": 2, "zoom_level": 5}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_control_camera_ptz_pan_only(self, mock_post):
        """Test control camera PTZ with pan only."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"pan_position": 2}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.control_camera_ptz(1, pan=2)

        assert result == {"pan_position": 2}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_control_camera_ptz_zoom_only(self, mock_post):
        """Test control camera PTZ with zoom only."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"zoom_level": 5}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.control_camera_ptz(1, zoom=5)

        assert result == {"zoom_level": 5}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_control_camera_ptz_error(self, mock_post):
        """Test control camera PTZ with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid PTZ command"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.control_camera_ptz(1, pan=2)

        assert "400" in str(exc_info.value)
        assert "Invalid PTZ command" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_control_camera_ptz_error_no_detail(self, mock_post):
        """Test control camera PTZ with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.control_camera_ptz(1, pan=2)

        assert "500" in str(exc_info.value)
        assert "PTZ control failed" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.put")
    def test_set_camera_password_success(self, mock_put):
        """Test successful set camera password."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"camera_id": 1, "has_password": True}
        mock_put.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.set_camera_password(1, "newpass", "oldpass")

        assert result == {"camera_id": 1, "has_password": True}
        mock_put.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.put")
    def test_set_camera_password_no_old(self, mock_put):
        """Test set camera password without old password."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"camera_id": 1, "has_password": True}
        mock_put.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.set_camera_password(1, "newpass")

        assert result == {"camera_id": 1, "has_password": True}
        mock_put.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.put")
    def test_set_camera_password_error(self, mock_put):
        """Test set camera password with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Incorrect password"}
        mock_put.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.set_camera_password(1, "newpass", "oldpass")

        assert "401" in str(exc_info.value)
        assert "Incorrect password" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.put")
    def test_set_camera_password_error_no_detail(self, mock_put):
        """Test set camera password with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_put.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.set_camera_password(1, "newpass")

        assert "500" in str(exc_info.value)
        assert "Failed to set password" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.delete")
    def test_delete_camera_password_success(self, mock_delete):
        """Test successful delete camera password."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"camera_id": 1, "has_password": False}
        mock_delete.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.delete_camera_password(1, "password")

        assert result == {"camera_id": 1, "has_password": False}
        mock_delete.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.delete")
    def test_delete_camera_password_error(self, mock_delete):
        """Test delete camera password with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Incorrect password"}
        mock_delete.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.delete_camera_password(1, "password")

        assert "401" in str(exc_info.value)
        assert "Incorrect password" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.delete")
    def test_delete_camera_password_error_no_detail(self, mock_delete):
        """Test delete camera password with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.delete_camera_password(1, "password")

        assert "500" in str(exc_info.value)
        assert "Failed to delete password" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_camera_thumbnails_success(self, mock_get):
        """Test successful get camera thumbnails."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "image_url": "url"}]
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.get_camera_thumbnails(1)

        assert result == [{"id": 1, "image_url": "url"}]
        mock_get.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_camera_thumbnails_error(self, mock_get):
        """Test get camera thumbnails with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Camera not found"}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_camera_thumbnails(1)

        assert "404" in str(exc_info.value)
        assert "Camera not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_camera_thumbnails_error_no_detail(self, mock_get):
        """Test get camera thumbnails with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_camera_thumbnails(1)

        assert "500" in str(exc_info.value)
        assert "Failed to get thumbnails" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_enable_camera_success(self, mock_post):
        """Test successful enable camera."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"camera_id": 1, "is_enabled": True}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.enable_camera(1)

        assert result == {"camera_id": 1, "is_enabled": True}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_enable_camera_error(self, mock_post):
        """Test enable camera with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Camera not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.enable_camera(1)

        assert "404" in str(exc_info.value)
        assert "Camera not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_enable_camera_error_no_detail(self, mock_post):
        """Test enable camera with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.enable_camera(1)

        assert "500" in str(exc_info.value)
        assert "Failed to enable camera" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disable_camera_success(self, mock_post):
        """Test successful disable camera."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"camera_id": 1, "is_enabled": False}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.disable_camera(1)

        assert result == {"camera_id": 1, "is_enabled": False}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disable_camera_error(self, mock_post):
        """Test disable camera with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Camera not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disable_camera(1)

        assert "404" in str(exc_info.value)
        assert "Camera not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disable_camera_error_no_detail(self, mock_post):
        """Test disable camera with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disable_camera(1)

        assert "500" in str(exc_info.value)
        assert "Failed to disable camera" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_list_sensors_success(self, mock_get):
        """Test successful list sensors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensors": []}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.list_sensors()

        assert result == {"sensors": []}
        mock_get.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.get")
    def test_list_sensors_error(self, mock_get):
        """Test list sensors with error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Server error"}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.list_sensors()

        assert "500" in str(exc_info.value)
        assert "Server error" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_list_sensors_error_no_detail(self, mock_get):
        """Test list sensors with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.list_sensors()

        assert "500" in str(exc_info.value)
        assert "Failed to list sensors" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_arm_motion_sensor_success(self, mock_post):
        """Test successful arm motion sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_armed": True}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.arm_motion_sensor(1)

        assert result == {"sensor_id": 1, "is_armed": True}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_arm_motion_sensor_error(self, mock_post):
        """Test arm motion sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm_motion_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_arm_motion_sensor_error_no_detail(self, mock_post):
        """Test arm motion sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm_motion_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to arm motion sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disarm_motion_sensor_success(self, mock_post):
        """Test successful disarm motion sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_armed": False}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.disarm_motion_sensor(1)

        assert result == {"sensor_id": 1, "is_armed": False}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disarm_motion_sensor_error(self, mock_post):
        """Test disarm motion sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm_motion_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disarm_motion_sensor_error_no_detail(self, mock_post):
        """Test disarm motion sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm_motion_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to disarm motion sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_trigger_motion_sensor_success(self, mock_post):
        """Test successful trigger motion sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_triggered": True}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.trigger_motion_sensor(1)

        assert result == {"sensor_id": 1, "is_triggered": True}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_trigger_motion_sensor_error(self, mock_post):
        """Test trigger motion sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.trigger_motion_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_trigger_motion_sensor_error_no_detail(self, mock_post):
        """Test trigger motion sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.trigger_motion_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to trigger motion sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_release_motion_sensor_success(self, mock_post):
        """Test successful release motion sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_triggered": False}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.release_motion_sensor(1)

        assert result == {"sensor_id": 1, "is_triggered": False}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_release_motion_sensor_error(self, mock_post):
        """Test release motion sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.release_motion_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_release_motion_sensor_error_no_detail(self, mock_post):
        """Test release motion sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.release_motion_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to release motion sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_arm_windoor_sensor_success(self, mock_post):
        """Test successful arm windoor sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_armed": True}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.arm_windoor_sensor(1)

        assert result == {"sensor_id": 1, "is_armed": True}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_arm_windoor_sensor_error(self, mock_post):
        """Test arm windoor sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm_windoor_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_arm_windoor_sensor_error_no_detail(self, mock_post):
        """Test arm windoor sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm_windoor_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to arm windoor sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disarm_windoor_sensor_success(self, mock_post):
        """Test successful disarm windoor sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_armed": False}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.disarm_windoor_sensor(1)

        assert result == {"sensor_id": 1, "is_armed": False}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disarm_windoor_sensor_error(self, mock_post):
        """Test disarm windoor sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm_windoor_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_disarm_windoor_sensor_error_no_detail(self, mock_post):
        """Test disarm windoor sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm_windoor_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to disarm windoor sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_open_windoor_sensor_success(self, mock_post):
        """Test successful open windoor sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_opened": True}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.open_windoor_sensor(1)

        assert result == {"sensor_id": 1, "is_opened": True}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_open_windoor_sensor_error(self, mock_post):
        """Test open windoor sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.open_windoor_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_open_windoor_sensor_error_no_detail(self, mock_post):
        """Test open windoor sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.open_windoor_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to open windoor sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_close_windoor_sensor_success(self, mock_post):
        """Test successful close windoor sensor."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_opened": False}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.close_windoor_sensor(1)

        assert result == {"sensor_id": 1, "is_opened": False}
        mock_post.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.post")
    def test_close_windoor_sensor_error(self, mock_post):
        """Test close windoor sensor with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.close_windoor_sensor(1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.post")
    def test_close_windoor_sensor_error_no_detail(self, mock_post):
        """Test close windoor sensor with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.close_windoor_sensor(1)

        assert "500" in str(exc_info.value)
        assert "Failed to close windoor sensor" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_sensor_status_success(self, mock_get):
        """Test successful get sensor status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensor_id": 1, "is_armed": True}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        result = client.get_sensor_status("motion", 1)

        assert result == {"sensor_id": 1, "is_armed": True}
        mock_get.assert_called_once()

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_sensor_status_error(self, mock_get):
        """Test get sensor status with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Sensor not found"}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_sensor_status("motion", 1)

        assert "404" in str(exc_info.value)
        assert "Sensor not found" in str(exc_info.value)

    @patch("frontend.surveillance_api_client.requests.get")
    def test_get_sensor_status_error_no_detail(self, mock_get):
        """Test get sensor status with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SurveillanceAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_sensor_status("motion", 1)

        assert "500" in str(exc_info.value)
        assert "Failed to get sensor status" in str(exc_info.value)
