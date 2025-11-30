"""API client for security operations."""

from datetime import datetime
from typing import Optional

import requests


class SecurityAPIClient:
    """Client for security API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client with base URL.

        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url.rstrip("/")

    def reconfirm(
        self,
        user_id: str,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> dict:
        """Reconfirm user with address and phone number.

        Args:
            user_id: User ID
            address: Optional address
            phone_number: Optional phone number

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If reconfirm fails
        """
        url = f"{self.base_url}/reconfirm/"
        payload = {"user_id": user_id}
        if address is not None:
            payload["address"] = address
        if phone_number is not None:
            payload["phone_number"] = phone_number
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Reconfirm failed")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def get_safety_zones(self, user_id: str) -> dict:
        """Get safety zones for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with safety zones list

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/get-safety-zones/"
        params = {"user_id": user_id}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to get safety zones")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def arm(self, user_id: str) -> dict:
        """Arm the security system.

        Args:
            user_id: User ID

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If arm fails
        """
        url = f"{self.base_url}/arm/"
        params = {"user_id": user_id}
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to arm system")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def disarm(self, user_id: str) -> dict:
        """Disarm the security system.

        Args:
            user_id: User ID

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If disarm fails
        """
        url = f"{self.base_url}/disarm/"
        params = {"user_id": user_id}
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to disarm system")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def arm_safety_zone(self, user_id: str, zone_name: str) -> dict:
        """Arm a safety zone.

        Args:
            user_id: User ID
            zone_name: Name of the safety zone

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If arm fails
        """
        url = f"{self.base_url}/arm-safety-zone/"
        payload = {"user_id": user_id, "name": zone_name, "device_ids": []}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to arm safety zone")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def disarm_safety_zone(self, user_id: str, zone_name: str) -> dict:
        """Disarm a safety zone.

        Args:
            user_id: User ID
            zone_name: Name of the safety zone

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If disarm fails
        """
        url = f"{self.base_url}/disarm-safety-zone/"
        payload = {"user_id": user_id, "name": zone_name, "device_ids": []}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to disarm safety zone")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def create_safety_zone(
        self, user_id: str, zone_name: str, device_ids: list[int]
    ) -> dict:
        """Create a new safety zone.

        Args:
            user_id: User ID
            zone_name: Name of the safety zone
            device_ids: List of device IDs to include in the zone

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If creation fails
        """
        url = f"{self.base_url}/create-safety-zone/"
        payload = {"user_id": user_id, "name": zone_name, "device_ids": device_ids}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to create safety zone")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def delete_safety_zone(self, user_id: str, zone_name: str) -> dict:
        """Delete a safety zone.

        Args:
            user_id: User ID
            zone_name: Name of the safety zone

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If deletion fails
        """
        url = f"{self.base_url}/delete-safety-zone/"
        payload = {"user_id": user_id, "name": zone_name, "device_ids": []}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to delete safety zone")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def update_safety_zone(
        self, user_id: str, zone_name: str, device_ids: list[int]
    ) -> dict:
        """Update an existing safety zone.

        Args:
            user_id: User ID
            zone_name: Name of the safety zone
            device_ids: List of device IDs to include in the zone

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If update fails
        """
        url = f"{self.base_url}/update-safety-zone/"
        payload = {"user_id": user_id, "name": zone_name, "device_ids": device_ids}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to update safety zone")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def configure_safehome_mode(
        self, user_id: str, mode_type: str, enabled_device_ids: list[int]
    ) -> dict:
        """Configure SafeHome mode.

        Args:
            user_id: User ID
            mode_type: Mode type (home, away, overnight_travel,
                extended_travel, guest_home)
            enabled_device_ids: List of device IDs to enable for this mode

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If configuration fails
        """
        url = f"{self.base_url}/configure-safehome-modes/"
        payload = {
            "user_id": user_id,
            "mode_type": mode_type,
            "enabled_device_ids": enabled_device_ids,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to configure mode")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def get_safehome_modes(self, user_id: str) -> dict:
        """Get SafeHome modes configuration.

        Args:
            user_id: User ID

        Returns:
            Dictionary with current mode and modes configuration

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/get-safehome-modes/"
        params = {"user_id": user_id}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to get modes")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def set_safehome_mode(self, user_id: str, mode_type: str) -> dict:
        """Set current SafeHome mode.

        Args:
            user_id: User ID
            mode_type: Mode type (home, away, overnight_travel,
                extended_travel, guest_home)

        Returns:
            Response with current mode and armed devices

        Raises:
            requests.HTTPException: If setting mode fails
        """
        url = f"{self.base_url}/set-safehome-mode/"
        payload = {"user_id": user_id, "mode_type": mode_type}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to set mode")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def alarm_condition(
        self,
        user_id: str,
        alarm_type: str,
        device_id: Optional[int],
        location: str,
        description: str,
    ) -> dict:
        """Report alarm condition.

        Args:
            user_id: User ID
            alarm_type: Type of alarm (intrusion, sensor_failure, panic,
                door_window_open)
            device_id: Optional device ID that triggered the alarm
            location: Location of the alarm
            description: Description of the alarm

        Returns:
            Response with event ID and actions taken

        Raises:
            requests.HTTPException: If alarm reporting fails
        """
        url = f"{self.base_url}/alarm-condition/"
        payload = {
            "user_id": user_id,
            "alarm_type": alarm_type,
            "device_id": device_id,
            "location": location,
            "description": description,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to report alarm")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def view_intrusion_log(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        alarm_type: Optional[str] = None,
    ) -> dict:
        """View intrusion log.

        Args:
            user_id: User ID
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            alarm_type: Optional alarm type for filtering

        Returns:
            Dictionary with total events and events list

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/view-intrusion-log/"
        payload = {"user_id": user_id}
        if start_date:
            payload["start_date"] = start_date.isoformat()
        if end_date:
            payload["end_date"] = end_date.isoformat()
        if alarm_type:
            payload["alarm_type"] = alarm_type
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to view log")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def panic_call(self, user_id: str, location: str) -> dict:
        """Call monitoring service through control panel (panic function).

        Args:
            user_id: User ID
            location: Location where panic was triggered

        Returns:
            Response with event ID and actions taken

        Raises:
            requests.HTTPException: If panic call fails
        """
        url = f"{self.base_url}/panic-call/"
        payload = {"user_id": user_id, "location": location}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to call panic")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def configure_safety_zone_interface(self, user_id: str) -> dict:
        """Get safety zone configuration interface data.

        Args:
            user_id: User ID

        Returns:
            Dictionary with available functions, existing zones, and available devices

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/configure-safety-zone/"
        params = {"user_id": user_id}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Failed to get configuration interface"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")
