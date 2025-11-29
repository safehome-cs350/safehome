"""Unit tests for control panel."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

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


@pytest.mark.parametrize(
    "button_name,number",
    [
        ("button1", "1"),
        ("button2", "2"),
        ("button3", "3"),
        ("button4", "4"),
        ("button5", "5"),
        ("button6", "6"),
        ("button7", "7"),
        ("button8", "8"),
        ("button9", "9"),
        ("button0", "0"),
    ],
)
def test_button_number_input_password_change_current(button_name, number):
    """Test number buttons in PASSWORD_CHANGE_CURRENT state."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_CURRENT
    button_method = getattr(control_panel, button_name)
    button_method()
    assert control_panel.button_sequence == number


@pytest.mark.parametrize(
    "button_name,number",
    [
        ("button1", "1"),
        ("button2", "2"),
        ("button3", "3"),
        ("button4", "4"),
        ("button5", "5"),
        ("button6", "6"),
        ("button7", "7"),
        ("button8", "8"),
        ("button9", "9"),
        ("button0", "0"),
    ],
)
def test_button_number_input_password_change_new(button_name, number):
    """Test number buttons in PASSWORD_CHANGE_NEW state."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_NEW
    button_method = getattr(control_panel, button_name)
    button_method()
    assert control_panel.button_sequence == number


@pytest.mark.parametrize(
    "button_name,number",
    [
        ("button1", "1"),
        ("button2", "2"),
        ("button3", "3"),
        ("button4", "4"),
        ("button5", "5"),
        ("button6", "6"),
        ("button7", "7"),
        ("button8", "8"),
        ("button9", "9"),
        ("button0", "0"),
    ],
)
def test_button_number_input_password_change_reconfirm(button_name, number):
    """Test number buttons in PASSWORD_CHANGE_RECONFIRM state."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_RECONFIRM
    button_method = getattr(control_panel, button_name)
    button_method()
    assert control_panel.button_sequence == number


@pytest.mark.parametrize(
    "button_name",
    [
        "button1",
        "button2",
        "button3",
        "button4",
        "button5",
        "button6",
        "button7",
        "button8",
        "button9",
        "button0",
        "button_star",
        "button_sharp",
    ],
)
def test_button_locked_no_action(button_name):
    """Test buttons in LOCKED state do nothing."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.LOCKED
    original_sequence = control_panel.button_sequence
    original_state = control_panel.state
    button_method = getattr(control_panel, button_name)
    button_method()
    assert control_panel.button_sequence == original_sequence
    assert control_panel.state == original_state


def test_button1_powered_off():
    """Test button1 in POWERED_OFF state calls power_on."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.POWERED_OFF
    with patch.object(control_panel, "power_on") as mock_power_on:
        control_panel.button1()
        mock_power_on.assert_called_once()


def test_button2_master():
    """Test button2 in MASTER state calls power_off."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    with patch.object(control_panel, "power_off") as mock_power_off:
        control_panel.button2()
        mock_power_off.assert_called_once()


def test_button3_master():
    """Test button3 in MASTER state calls reset."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    with patch.object(control_panel, "reset") as mock_reset:
        control_panel.button3()
        mock_reset.assert_called_once()


def test_button4_master():
    """Test button4 in MASTER state calls arm."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    with patch.object(control_panel, "arm") as mock_arm:
        control_panel.button4()
        mock_arm.assert_called_once()


def test_button5_master():
    """Test button5 in MASTER state calls disarm."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    with patch.object(control_panel, "disarm") as mock_disarm:
        control_panel.button5()
        mock_disarm.assert_called_once()


def test_button6_master():
    """Test button6 in MASTER state changes to PASSWORD_CHANGE_CURRENT."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button6()
    assert control_panel.state == ControlPanelState.PASSWORD_CHANGE_CURRENT
    assert control_panel.button_sequence == ""


def test_button_star_not_powered_off():
    """Test button_star not in POWERED_OFF calls panic."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.IDLE
    with patch.object(control_panel, "panic") as mock_panic:
        control_panel.button_star()
        mock_panic.assert_called_once()


def test_button_star_powered_off():
    """Test button_star in POWERED_OFF does nothing."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.POWERED_OFF
    with patch.object(control_panel, "panic") as mock_panic:
        control_panel.button_star()
        mock_panic.assert_not_called()


def test_button_sharp():
    """Test button_sharp resets sequence and state."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER
    control_panel.button_sequence = "123"
    control_panel.button_sharp()
    assert control_panel.button_sequence == ""
    assert control_panel.state == ControlPanelState.IDLE


def test_handle_wrong_password_password_change():
    """Test handle_wrong_password() increments fail_count."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.PASSWORD_CHANGE_CURRENT
    control_panel.handle_wrong_password()
    assert control_panel.fail_count == 1


def test_unlock():
    """Test unlock() changes state to IDLE."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.LOCKED
    control_panel.unlock()
    assert control_panel.state == ControlPanelState.IDLE


def test_power_on():
    """Test power_on() changes state to IDLE."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.POWERED_OFF

    with patch("httpx.post") as mock_post:
        control_panel.power_on()

        mock_post.assert_called_once_with(
            f"{control_panel.SERVER_URL}/power-on/",
            json={"user_id": control_panel.user_id},
        )
        assert control_panel.state == ControlPanelState.IDLE


def test_power_off():
    """Test power_off() changes state to POWERED_OFF."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER

    with patch("httpx.post") as mock_post:
        control_panel.power_off()

        mock_post.assert_called_once_with(
            f"{control_panel.SERVER_URL}/power-off/",
            json={"user_id": control_panel.user_id},
        )
        assert control_panel.state == ControlPanelState.POWERED_OFF


def test_reset():
    """Test reset() changes state to IDLE."""
    control_panel = ControlPanel()
    control_panel.state = ControlPanelState.MASTER

    with patch("httpx.post") as mock_post:
        control_panel.reset()

        assert mock_post.call_count == 2
        mock_post.assert_any_call(
            f"{control_panel.SERVER_URL}/power-off/",
            json={"user_id": control_panel.user_id},
        )
        mock_post.assert_any_call(
            f"{control_panel.SERVER_URL}/power-on/",
            json={"user_id": control_panel.user_id},
        )
        assert control_panel.state == ControlPanelState.IDLE


def test_arm_success():
    """Test arm() sends arm command."""
    control_panel = ControlPanel()

    with patch.object(control_panel, "set_armed_led") as mock_armed_led:
        with patch("httpx.post") as mock_post:
            control_panel.arm()

            mock_post.assert_called_once_with(
                f"{control_panel.SERVER_URL}/arm/?user_id={control_panel.user_id}"
            )
        mock_armed_led.assert_called_once_with(True)


def test_arm_fail():
    """Test arm() handles HTTP error."""
    control_panel = ControlPanel()

    with patch.object(control_panel, "set_armed_led") as mock_armed_led:
        with patch("httpx.post") as mock_post:
            mock_post.side_effect = httpx.HTTPError("Error")
            control_panel.arm()

            mock_post.assert_called_once_with(
                f"{control_panel.SERVER_URL}/arm/?user_id={control_panel.user_id}"
            )
        mock_armed_led.assert_not_called()


def test_disarm_success():
    """Test disarm() sends disarm command."""
    control_panel = ControlPanel()

    with patch.object(control_panel, "set_armed_led") as mock_armed_led:
        with patch("httpx.post") as mock_post:
            control_panel.disarm()

            mock_post.assert_called_once_with(
                f"{control_panel.SERVER_URL}/disarm/?user_id={control_panel.user_id}"
            )
        mock_armed_led.assert_called_once_with(False)


def test_disarm_fail():
    """Test disarm() handles HTTP error."""
    control_panel = ControlPanel()

    with patch.object(control_panel, "set_armed_led") as mock_armed_led:
        with patch("httpx.post") as mock_post:
            mock_post.side_effect = httpx.HTTPError("Error")
            control_panel.disarm()

            mock_post.assert_called_once_with(
                f"{control_panel.SERVER_URL}/disarm/?user_id={control_panel.user_id}"
            )
        mock_armed_led.assert_not_called()


def test_handle_number_input_idle():
    """Test handle_number_input() in IDLE state."""
    control_panel = ControlPanel()
    control_panel.handle_number_input("1")

    assert control_panel.button_sequence == "1"
    assert control_panel.state == ControlPanelState.IDLE
