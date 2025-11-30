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

    def get_camera_view(self, camera_id: int, password: Optional[str] = None) -> dict:
        """Get camera view with current settings.

        Args:
            camera_id: Camera identifier
            password: Optional password if camera is password protected

        Returns:
            Camera view data including base64 image

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/view"
        params = {}
        if password is not None:
            params["password"] = password
        response = requests.get(url, params=params)
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

    def set_camera_password(
        self, camera_id: int, new_password: str, old_password: str | None = None
    ) -> dict:
        """Set password for a camera.

        Args:
            camera_id: Camera identifier
            new_password: New password to set
            old_password: Old password (required if camera already has a password)

        Returns:
            Camera password status

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/password"
        payload = {"new_password": new_password}
        if old_password is not None:
            payload["old_password"] = old_password
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to set password")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def delete_camera_password(self, camera_id: int, password: str) -> dict:
        """Delete password for a camera.

        Args:
            camera_id: Camera identifier
            password: Password to verify before deletion

        Returns:
            Camera password status

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/cameras/{camera_id}/password"
        params = {"password": password}
        response = requests.delete(url, params=params)
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

    # Sensor API methods

    def list_sensors(self) -> dict:
        """List all available sensors.

        Returns:
            Dictionary with sensors list

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to list sensors")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def arm_motion_sensor(self, sensor_id: int) -> dict:
        """Arm a motion sensor.

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/motion/{sensor_id}/arm"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to arm motion sensor")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def disarm_motion_sensor(self, sensor_id: int) -> dict:
        """Disarm a motion sensor.

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/motion/{sensor_id}/disarm"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Failed to disarm motion sensor"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def trigger_motion_sensor(self, sensor_id: int) -> dict:
        """Trigger a motion sensor (simulate motion detection).

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/motion/{sensor_id}/trigger"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Failed to trigger motion sensor"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def release_motion_sensor(self, sensor_id: int) -> dict:
        """Release a motion sensor (clear motion detection).

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/motion/{sensor_id}/release"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Failed to release motion sensor"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def arm_windoor_sensor(self, sensor_id: int) -> dict:
        """Arm a window/door sensor.

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/windoor/{sensor_id}/arm"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to arm windoor sensor")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def disarm_windoor_sensor(self, sensor_id: int) -> dict:
        """Disarm a window/door sensor.

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/windoor/{sensor_id}/disarm"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Failed to disarm windoor sensor"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def open_windoor_sensor(self, sensor_id: int) -> dict:
        """Open a window/door sensor (simulate opening).

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/windoor/{sensor_id}/open"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Failed to open windoor sensor"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def close_windoor_sensor(self, sensor_id: int) -> dict:
        """Close a window/door sensor (simulate closing).

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor state response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/windoor/{sensor_id}/close"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get(
                "detail", "Failed to close windoor sensor"
            )
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")

    def get_sensor_status(self, sensor_type: str, sensor_id: int) -> dict:
        """Get detailed sensor status.

        Args:
            sensor_type: Sensor type ("motion" or "windoor")
            sensor_id: Sensor identifier

        Returns:
            Sensor status response

        Raises:
            requests.HTTPException: If request fails
        """
        url = f"{self.base_url}/surveillance/sensors/{sensor_type}/{sensor_id}/status"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Failed to get sensor status")
            raise requests.HTTPError(f"{response.status_code}: {error_detail}")
