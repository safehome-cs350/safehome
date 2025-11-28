"""Unit tests for control panel."""

from unittest.mock import MagicMock, patch

import httpx

from control_panel.control_panel import ControlPanel, ControlPanelState


def test_check_password_master_success():
    """Test check_password() for master login."""
    control_panel = ControlPanel()
    control_panel.button_sequence = "1234"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = "master"
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.check_password()

        assert control_panel.state == ControlPanelState.MASTER


def test_check_password_guest_success():
    """Test check_password() for guest login."""
    control_panel = ControlPanel()
    control_panel.button_sequence = "5678"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = "guest"
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.check_password()

        assert control_panel.state == ControlPanelState.GUEST


def test_check_password_fail_count_less_than_3():
    """Test check_password() with fail_count < 3."""
    control_panel = ControlPanel()
    control_panel.button_sequence = "1234"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_request = MagicMock()
        mock_resp = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=mock_request, response=mock_resp
        )
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.check_password()

        assert control_panel.state == ControlPanelState.IDLE


def test_check_password_fail_count_3():
    """Test check_password() with fail_count == 3."""
    control_panel = ControlPanel()
    control_panel.button_sequence = "1234"
    control_panel.fail_count = 2

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_request = MagicMock()
        mock_resp = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=mock_request, response=mock_resp
        )
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.check_password()

        assert control_panel.fail_count == 0
        assert control_panel.state == ControlPanelState.LOCKED


def test_check_password_request_error():
    """Test check_password() with RequestError."""
    control_panel = ControlPanel()
    control_panel.button_sequence = "1234"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.RequestError("Error")
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.check_password()

        assert control_panel.state == ControlPanelState.IDLE


def test_password_change_check_password_master_success():
    """Test password_change_check_password() for master login success."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button_sequence = "1234"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = "master"
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_check_password()

        assert control_panel.state == ControlPanelState.PASSWORD_CHANGE_NEW


def test_password_change_check_password_wrong_role():
    """Test password_change_check_password() with wrong role."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button_sequence = "1234"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = "guest"
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_check_password()

        assert control_panel.state == ControlPanelState.MASTER
        assert control_panel.fail_count == 1


def test_password_change_check_password_fail_count_3():
    """Test password_change_check_password() with fail_count == 3."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button_sequence = "1234"
    control_panel.fail_count = 2

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = "guest"
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_check_password()

        assert control_panel.fail_count == 0
        assert control_panel.state == ControlPanelState.LOCKED


def test_password_change_check_password_http_status_error_less_than_3():
    """Test password_change_check_password() with HTTPStatusError, fail_count < 3."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button_sequence = "1234"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_request = MagicMock()
        mock_resp = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=mock_request, response=mock_resp
        )
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_check_password()

        assert control_panel.state == ControlPanelState.MASTER
        assert control_panel.fail_count == 1


def test_password_change_check_password_http_status_error_3():
    """Test password_change_check_password() with HTTPStatusError, fail_count == 3."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button_sequence = "1234"
    control_panel.fail_count = 2

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_request = MagicMock()
        mock_resp = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=mock_request, response=mock_resp
        )
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_check_password()

        assert control_panel.fail_count == 0
        assert control_panel.state == ControlPanelState.LOCKED


def test_password_change_check_password_request_error():
    """Test password_change_check_password() with RequestError."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button_sequence = "1234"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.RequestError("Error")
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_check_password()

        assert control_panel.state == ControlPanelState.MASTER


def test_password_change_new_password_success():
    """Test password_change_new_password() success."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_NEW
    control_panel.button_sequence = "5678"

    control_panel.password_change_new_password()

    assert control_panel.state == ControlPanelState.PASSWORD_CHANGE_RECONFIRM
    assert control_panel.new_password == "5678"
    assert control_panel.button_sequence == ""


def test_password_change_reconfirm_password_match_success():
    """Test reconfirm with matching passwords and server success."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_RECONFIRM
    control_panel.button_sequence = "5678"
    control_panel.new_password = "5678"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_reconfirm_password()

        assert control_panel.state == ControlPanelState.MASTER
        assert control_panel.button_sequence == ""


def test_password_change_reconfirm_password_match_server_error():
    """Test reconfirm with matching passwords and server error."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_RECONFIRM
    control_panel.button_sequence = "5678"
    control_panel.new_password = "5678"

    with patch("httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPError("Error")
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        control_panel.password_change_reconfirm_password()

        assert control_panel.state == ControlPanelState.MASTER
        assert control_panel.button_sequence == ""


def test_password_change_reconfirm_password_mismatch():
    """Test reconfirm with mismatched passwords."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_RECONFIRM
    control_panel.button_sequence = "1234"
    control_panel.new_password = "5678"

    control_panel.password_change_reconfirm_password()

    assert control_panel.state == ControlPanelState.PASSWORD_CHANGE_NEW
    assert control_panel.button_sequence == ""
