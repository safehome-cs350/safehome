"""Tests for common API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from frontend.common_api_client import CommonAPIClient


class TestCommonAPIClient:
    """Test cases for CommonAPIClient class."""

    def test_init(self):
        """Test CommonAPIClient initialization."""
        client = CommonAPIClient()
        assert client.base_url == "http://localhost:8000"

        client = CommonAPIClient("http://example.com")
        assert client.base_url == "http://example.com"

        client = CommonAPIClient("http://example.com/")
        assert client.base_url == "http://example.com"

    @patch("frontend.common_api_client.requests.post")
    def test_login_success(self, mock_post):
        """Test successful login."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '"Welcome!"'
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        result = client.login("user1", "pass1", "pass2")

        assert result == {"message": "Welcome!"}
        mock_post.assert_called_once()

    @patch("frontend.common_api_client.requests.post")
    def test_login_error(self, mock_post):
        """Test login with error response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid credentials"}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.login("user1", "pass1", "pass2")

        assert "401" in str(exc_info.value)
        assert "Invalid credentials" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.post")
    def test_login_error_no_detail(self, mock_post):
        """Test login with error response without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.login("user1", "pass1", "pass2")

        assert "500" in str(exc_info.value)
        assert "Login failed" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.get")
    def test_get_config_success(self, mock_get):
        """Test successful get config."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"password1": "pass1", "delay_time": 300}
        mock_get.return_value = mock_response

        client = CommonAPIClient()
        result = client.get_config("user1")

        assert result == {"password1": "pass1", "delay_time": 300}
        mock_get.assert_called_once()

    @patch("frontend.common_api_client.requests.get")
    def test_get_config_error(self, mock_get):
        """Test get config with error response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user ID"}
        mock_get.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_config("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user ID" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.get")
    def test_get_config_error_no_detail(self, mock_get):
        """Test get config with error response without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.get_config("user1")

        assert "500" in str(exc_info.value)
        assert "Configuration retrieval failed" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.post")
    def test_config_success(self, mock_post):
        """Test successful config update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Configuration updated"}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        result = client.config(
            "user1",
            password1="newpass1",
            delay_time=600,
            phone_number="1234567890",
        )

        assert result == {"message": "Configuration updated"}
        mock_post.assert_called_once()

    @patch("frontend.common_api_client.requests.post")
    def test_config_error(self, mock_post):
        """Test config update with error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Delay time must be at least 300"}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.config("user1", delay_time=200)

        assert "400" in str(exc_info.value)
        assert "Delay time must be at least 300" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.post")
    def test_config_error_no_detail(self, mock_post):
        """Test config update with error response without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.config("user1")

        assert "500" in str(exc_info.value)
        assert "Configuration update failed" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.post")
    def test_power_on_success(self, mock_post):
        """Test successful power on."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "System powered on"}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        result = client.power_on("user1")

        assert result == {"message": "System powered on"}
        mock_post.assert_called_once()

    @patch("frontend.common_api_client.requests.post")
    def test_power_on_error(self, mock_post):
        """Test power on with error response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user ID"}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.power_on("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user ID" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.post")
    def test_power_on_error_no_detail(self, mock_post):
        """Test power on with error response without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.power_on("user1")

        assert "500" in str(exc_info.value)
        assert "Power on failed" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.post")
    def test_power_off_success(self, mock_post):
        """Test successful power off."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "System powered off"}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        result = client.power_off("user1")

        assert result == {"message": "System powered off"}
        mock_post.assert_called_once()

    @patch("frontend.common_api_client.requests.post")
    def test_power_off_error(self, mock_post):
        """Test power off with error response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid user ID"}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.power_off("user1")

        assert "401" in str(exc_info.value)
        assert "Invalid user ID" in str(exc_info.value)

    @patch("frontend.common_api_client.requests.post")
    def test_power_off_error_no_detail(self, mock_post):
        """Test power off with error response without detail."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = CommonAPIClient()
        with pytest.raises(requests.HTTPError) as exc_info:
            client.power_off("user1")

        assert "500" in str(exc_info.value)
        assert "Power off failed" in str(exc_info.value)
