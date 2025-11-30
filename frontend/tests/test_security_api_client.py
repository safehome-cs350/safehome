"""Tests for security API client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from frontend.security_api_client import SecurityAPIClient


class TestSecurityAPIClient:
    """Test cases for SecurityAPIClient class."""

    def test_init(self):
        """Test SecurityAPIClient initialization."""
        client = SecurityAPIClient()
        assert client.base_url == "http://localhost:8000"

        client = SecurityAPIClient("http://example.com")
        assert client.base_url == "http://example.com"

        client = SecurityAPIClient("http://example.com/")
        assert client.base_url == "http://example.com"

    @patch("frontend.security_api_client.requests.post")
    def test_reconfirm_success(self, mock_post):
        """Test successful reconfirm."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Reconfirmed"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.reconfirm(
            "user1", address="123 Main St", phone_number="1234567890"
        )

        assert result == {"message": "Reconfirmed"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_reconfirm_error(self, mock_post):
        """Test reconfirm with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.reconfirm("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_reconfirm_error_no_detail(self, mock_post):
        """Test reconfirm with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.reconfirm("user1")

        assert "500" in str(exc_info.value)
        assert "Reconfirm failed" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.get")
    def test_get_safety_zones_success(self, mock_get):
        """Test successful get safety zones."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"safety_zones": []}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        result = client.get_safety_zones("user1")

        assert result == {"safety_zones": []}
        mock_get.assert_called_once()

    @patch("frontend.security_api_client.requests.get")
    def test_get_safety_zones_error(self, mock_get):
        """Test get safety zones with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_safety_zones("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.get")
    def test_get_safety_zones_error_no_detail(self, mock_get):
        """Test get safety zones with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_safety_zones("user1")

        assert "500" in str(exc_info.value)
        assert "Failed to get safety zones" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_arm_success(self, mock_post):
        """Test successful arm."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Armed"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.arm("user1")

        assert result == {"message": "Armed"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_arm_error(self, mock_post):
        """Test arm with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_arm_error_no_detail(self, mock_post):
        """Test arm with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm("user1")

        assert "500" in str(exc_info.value)
        assert "Failed to arm system" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_disarm_success(self, mock_post):
        """Test successful disarm."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Disarmed"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.disarm("user1")

        assert result == {"message": "Disarmed"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_disarm_error(self, mock_post):
        """Test disarm with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_disarm_error_no_detail(self, mock_post):
        """Test disarm with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm("user1")

        assert "500" in str(exc_info.value)
        assert "Failed to disarm system" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_arm_safety_zone_success(self, mock_post):
        """Test successful arm safety zone."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Zone armed"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.arm_safety_zone("user1", "zone1")

        assert result == {"message": "Zone armed"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_arm_safety_zone_error(self, mock_post):
        """Test arm safety zone with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Zone not found"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm_safety_zone("user1", "zone1")

        assert "404" in str(exc_info.value)
        assert "Zone not found" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_arm_safety_zone_error_no_detail(self, mock_post):
        """Test arm safety zone with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.arm_safety_zone("user1", "zone1")

        assert "500" in str(exc_info.value)
        assert "Failed to arm safety zone" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_disarm_safety_zone_success(self, mock_post):
        """Test successful disarm safety zone."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Zone disarmed"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.disarm_safety_zone("user1", "zone1")

        assert result == {"message": "Zone disarmed"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_disarm_safety_zone_error(self, mock_post):
        """Test disarm safety zone with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Zone not found"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm_safety_zone("user1", "zone1")

        assert "404" in str(exc_info.value)
        assert "Zone not found" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_disarm_safety_zone_error_no_detail(self, mock_post):
        """Test disarm safety zone with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.disarm_safety_zone("user1", "zone1")

        assert "500" in str(exc_info.value)
        assert "Failed to disarm safety zone" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_create_safety_zone_success(self, mock_post):
        """Test successful create safety zone."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Zone created"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.create_safety_zone("user1", "zone1", [1, 2, 3])

        assert result == {"message": "Zone created"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_create_safety_zone_error(self, mock_post):
        """Test create safety zone with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid zone name"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.create_safety_zone("user1", "zone1", [1, 2, 3])

        assert "400" in str(exc_info.value)
        assert "Invalid zone name" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_create_safety_zone_error_no_detail(self, mock_post):
        """Test create safety zone with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.create_safety_zone("user1", "zone1", [1, 2, 3])

        assert "500" in str(exc_info.value)
        assert "Failed to create safety zone" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_delete_safety_zone_success(self, mock_post):
        """Test successful delete safety zone."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Zone deleted"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.delete_safety_zone("user1", "zone1")

        assert result == {"message": "Zone deleted"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_delete_safety_zone_error(self, mock_post):
        """Test delete safety zone with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Zone not found"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.delete_safety_zone("user1", "zone1")

        assert "404" in str(exc_info.value)
        assert "Zone not found" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_delete_safety_zone_error_no_detail(self, mock_post):
        """Test delete safety zone with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.delete_safety_zone("user1", "zone1")

        assert "500" in str(exc_info.value)
        assert "Failed to delete safety zone" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_update_safety_zone_success(self, mock_post):
        """Test successful update safety zone."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Zone updated"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.update_safety_zone("user1", "zone1", [1, 2, 3])

        assert result == {"message": "Zone updated"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_update_safety_zone_error(self, mock_post):
        """Test update safety zone with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Zone not found"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.update_safety_zone("user1", "zone1", [1, 2, 3])

        assert "404" in str(exc_info.value)
        assert "Zone not found" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_update_safety_zone_error_no_detail(self, mock_post):
        """Test update safety zone with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.update_safety_zone("user1", "zone1", [1, 2, 3])

        assert "500" in str(exc_info.value)
        assert "Failed to update safety zone" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_configure_safehome_mode_success(self, mock_post):
        """Test successful configure safehome mode."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Mode configured"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.configure_safehome_mode("user1", "home", [1, 2, 3])

        assert result == {"message": "Mode configured"}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_configure_safehome_mode_error(self, mock_post):
        """Test configure safehome mode with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid mode"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.configure_safehome_mode("user1", "home", [1, 2, 3])

        assert "400" in str(exc_info.value)
        assert "Invalid mode" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_configure_safehome_mode_error_no_detail(self, mock_post):
        """Test configure safehome mode with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.configure_safehome_mode("user1", "home", [1, 2, 3])

        assert "500" in str(exc_info.value)
        assert "Failed to configure mode" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.get")
    def test_get_safehome_modes_success(self, mock_get):
        """Test successful get safehome modes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_mode": "home", "modes": {}}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        result = client.get_safehome_modes("user1")

        assert result == {"current_mode": "home", "modes": {}}
        mock_get.assert_called_once()

    @patch("frontend.security_api_client.requests.get")
    def test_get_safehome_modes_error(self, mock_get):
        """Test get safehome modes with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_safehome_modes("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.get")
    def test_get_safehome_modes_error_no_detail(self, mock_get):
        """Test get safehome modes with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_safehome_modes("user1")

        assert "500" in str(exc_info.value)
        assert "Failed to get modes" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_set_safehome_mode_success(self, mock_post):
        """Test successful set safehome mode."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_mode": "home", "armed_devices": []}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.set_safehome_mode("user1", "home")

        assert result == {"current_mode": "home", "armed_devices": []}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_set_safehome_mode_error(self, mock_post):
        """Test set safehome mode with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid mode"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.set_safehome_mode("user1", "home")

        assert "400" in str(exc_info.value)
        assert "Invalid mode" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_set_safehome_mode_error_no_detail(self, mock_post):
        """Test set safehome mode with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.set_safehome_mode("user1", "home")

        assert "500" in str(exc_info.value)
        assert "Failed to set mode" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_alarm_condition_success(self, mock_post):
        """Test successful alarm condition."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"event_id": 1, "actions": []}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.alarm_condition(
            "user1", "intrusion", 1, "location", "description"
        )

        assert result == {"event_id": 1, "actions": []}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_alarm_condition_error(self, mock_post):
        """Test alarm condition with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.alarm_condition("user1", "intrusion", 1, "location", "description")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_alarm_condition_error_no_detail(self, mock_post):
        """Test alarm condition with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.alarm_condition("user1", "intrusion", 1, "location", "description")

        assert "500" in str(exc_info.value)
        assert "Failed to report alarm" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_view_intrusion_log_success(self, mock_post):
        """Test successful view intrusion log."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_events": 0, "events": []}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        result = client.view_intrusion_log("user1", start_date, end_date, "intrusion")

        assert result == {"total_events": 0, "events": []}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_view_intrusion_log_error(self, mock_post):
        """Test view intrusion log with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.view_intrusion_log("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_view_intrusion_log_error_no_detail(self, mock_post):
        """Test view intrusion log with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.view_intrusion_log("user1")

        assert "500" in str(exc_info.value)
        assert "Failed to view log" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_panic_call_success(self, mock_post):
        """Test successful panic call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"event_id": 1, "actions": []}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        result = client.panic_call("user1", "location")

        assert result == {"event_id": 1, "actions": []}
        mock_post.assert_called_once()

    @patch("frontend.security_api_client.requests.post")
    def test_panic_call_error(self, mock_post):
        """Test panic call with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.panic_call("user1", "location")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.post")
    def test_panic_call_error_no_detail(self, mock_post):
        """Test panic call with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.panic_call("user1", "location")

        assert "500" in str(exc_info.value)
        assert "Failed to call panic" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.get")
    def test_configure_safety_zone_interface_success(self, mock_get):
        """Test successful configure safety zone interface."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"functions": [], "zones": [], "devices": []}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        result = client.configure_safety_zone_interface("user1")

        assert result == {"functions": [], "zones": [], "devices": []}
        mock_get.assert_called_once()

    @patch("frontend.security_api_client.requests.get")
    def test_configure_safety_zone_interface_error(self, mock_get):
        """Test configure safety zone interface with error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user"}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.configure_safety_zone_interface("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user" in str(exc_info.value)

    @patch("frontend.security_api_client.requests.get")
    def test_configure_safety_zone_interface_error_no_detail(self, mock_get):
        """Test configure safety zone interface with error without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = SecurityAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.configure_safety_zone_interface("user1")

        assert "500" in str(exc_info.value)
        assert "Failed to get configuration interface" in str(exc_info.value)
