"""API client for common system operations."""

from typing import Optional

import requests


class CommonAPIClient:
    """Client for common system API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client with base URL.

        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url.rstrip("/")

    def login(self, user_id: str, password1: str, password2: str) -> dict:
        """Login to the system.

        Args:
            user_id: User ID
            password1: First password
            password2: Second password

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If login fails
        """
        url = f"{self.base_url}/login/"
        payload = {
            "user_id": user_id,
            "password1": password1,
            "password2": password2,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return {"message": response.text.strip('"')}
        else:
            error_detail = response.json().get("detail", "Login failed")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def get_config(self, user_id: str) -> dict:
        """Get system configuration.

        Args:
            user_id: User ID

        Returns:
            Configuration data from the API

        Raises:
            requests.HTTPException: If config retrieval fails
        """
        url = f"{self.base_url}/config/"
        payload = {"user_id": user_id}
        response = requests.get(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Configuration retrieval failed"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def config(
        self,
        user_id: str,
        password1: Optional[str] = None,
        password2: Optional[str] = None,
        master_password: Optional[str] = None,
        guest_password: Optional[str] = None,
        delay_time: Optional[int] = None,
        phone_number: Optional[str] = None,
    ) -> dict:
        """Update system configuration.

        Args:
            user_id: User ID
            password1: Optional new password1
            password2: Optional new password2
            master_password: Optional new master password
            guest_password: Optional new guest password
            delay_time: Optional new delay time (must be at least 300)
            phone_number: Optional new phone number

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If config update fails
        """
        url = f"{self.base_url}/config/"
        payload = {"user_id": user_id}
        payload["password1"] = password1
        payload["password2"] = password2
        payload["master_password"] = master_password
        payload["guest_password"] = guest_password
        payload["delay_time"] = delay_time
        payload["phone_number"] = phone_number

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Configuration update failed")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def power_on(self, user_id: str) -> dict:
        """Turn the system on.

        Args:
            user_id: User ID

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If power on fails
        """
        url = f"{self.base_url}/power-on/"
        payload = {"user_id": user_id}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Power on failed")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def power_off(self, user_id: str) -> dict:
        """Turn the system off.

        Args:
            user_id: User ID

        Returns:
            Response message from the API

        Raises:
            requests.HTTPException: If power off fails
        """
        url = f"{self.base_url}/power-off/"
        payload = {"user_id": user_id}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Power off failed")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")
