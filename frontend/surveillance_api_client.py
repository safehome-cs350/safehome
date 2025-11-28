"""API client for surveillance operations."""

from typing import Optional

import requests


class SurveillanceAPIClient:
    """Client for surveillance API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client with base URL.

        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url.rstrip("/")

    def list_cameras(self) -> dict:
        """List all available cameras.

        Returns:
            Dictionary with cameras list

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to list cameras")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def get_camera_view(self, camera_id: int) -> dict:
        """Get camera view with current settings.

        Args:
            camera_id: Camera identifier

        Returns:
            Camera view data including base64 image

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/view"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to get camera view")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def control_camera_ptz(
        self, camera_id: int, pan: Optional[int] = None, zoom: Optional[int] = None
    ) -> dict:
        """Control camera PTZ (Pan-Tilt-Zoom).

        Args:
            camera_id: Camera identifier
            pan: Target pan position (-5 to 5)
            zoom: Target zoom level (1 to 9)

        Returns:
            PTZ response with current position and status

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/ptz"
        payload = {}
        if pan is not None:
            payload["pan"] = pan
        if zoom is not None:
            payload["zoom"] = zoom
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "PTZ control failed")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def set_camera_password(self, camera_id: int, password: str) -> dict:
        """Set password for a camera.

        Args:
            camera_id: Camera identifier
            password: Password to set

        Returns:
            Camera password status

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/password"
        payload = {"password": password}
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to set password")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def delete_camera_password(self, camera_id: int) -> dict:
        """Delete password for a camera.

        Args:
            camera_id: Camera identifier

        Returns:
            Camera password status

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/password"
        response = requests.delete(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to delete password")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def get_camera_thumbnails(self, camera_id: int) -> list:
        """Get camera thumbnail history.

        Args:
            camera_id: Camera identifier

        Returns:
            List of thumbnail shots

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/thumbnails"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to get thumbnails")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def enable_camera(self, camera_id: int) -> dict:
        """Enable a camera.

        Args:
            camera_id: Camera identifier

        Returns:
            Camera state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/enable"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to enable camera")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def disable_camera(self, camera_id: int) -> dict:
        """Disable a camera.

        Args:
            camera_id: Camera identifier

        Returns:
            Camera state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/disable"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to disable camera")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")
