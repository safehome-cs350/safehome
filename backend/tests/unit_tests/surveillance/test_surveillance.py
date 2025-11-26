"""Tests for the surveillance API module."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
import pytest
import base64

from backend.app import app

client = TestClient(app)


class TestCameraList:
    """Test camera list endpoint."""
    
    def test_list_cameras_success(self):
        """Test successful camera list retrieval."""
        response = client.get("/surveillance/cameras")
        assert response.status_code == 200
        
        data = response.json()
        assert "cameras" in data
        assert len(data["cameras"]) > 0
        
        # Check camera structure
        camera = data["cameras"][0]
        required_fields = ["camera_id", "name", "location", "is_enabled", "is_online", "has_password"]
        for field in required_fields:
            assert field in camera


class TestCameraView:
    """Test camera view endpoints."""
    
    def test_get_camera_view_enabled(self):
        """Test getting view from enabled camera."""
        response = client.get("/surveillance/cameras/1/view")
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_id"] == 1
        assert data["name"] == "거실 카메라"
        assert data["is_enabled"] == True
        assert data["is_online"] == True
        assert "current_view_base64" in data
        assert data["current_view_base64"] is not None
        
        # Verify base64 image data
        try:
            base64.b64decode(data["current_view_base64"])
        except Exception:
            pytest.fail("Invalid base64 image data")
    
    def test_get_camera_view_disabled(self):
        """Test getting view from disabled camera."""
        response = client.get("/surveillance/cameras/3/view")
        assert response.status_code == 400
        assert "disabled" in response.json()["detail"]
    
    def test_get_camera_view_not_found(self):
        """Test getting view from non-existent camera."""
        response = client.get("/surveillance/cameras/999/view")
        assert response.status_code == 404
        assert response.json()["detail"] == "Camera not found"


class TestPTZControl:
    """Test PTZ (Pan-Tilt-Zoom) control endpoints."""
    
    def test_ptz_pan_control(self):
        """Test camera pan control."""
        response = client.post("/surveillance/cameras/1/ptz", json={"pan": 2})
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_id"] == 1
        assert "pan_position" in data
        assert "zoom_level" in data
        assert data["success"] == True
    
    def test_ptz_zoom_control(self):
        """Test camera zoom control."""
        response = client.post("/surveillance/cameras/1/ptz", json={"zoom": 5})
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_id"] == 1
        assert "zoom_level" in data
        assert data["success"] == True
    
    def test_ptz_combined_control(self):
        """Test combined pan and zoom control."""
        response = client.post("/surveillance/cameras/1/ptz", json={"pan": 1, "zoom": 3})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "pan_position" in data
        assert "zoom_level" in data
    
    def test_ptz_disabled_camera(self):
        """Test PTZ control on disabled camera."""
        response = client.post("/surveillance/cameras/3/ptz", json={"pan": 1})
        assert response.status_code == 400
        assert "disabled" in response.json()["detail"]


class TestCameraPassword:
    """Test camera password management."""
    
    def test_set_camera_password(self):
        """Test setting camera password."""
        response = client.put("/surveillance/cameras/1/password", json={"password": "test123"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_id"] == 1
        assert data["has_password"] == True
    
    def test_delete_camera_password(self):
        """Test deleting camera password."""
        response = client.delete("/surveillance/cameras/1/password")
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_id"] == 1
        assert data["has_password"] == False


class TestCameraState:
    """Test camera enable/disable functionality."""
    
    def test_enable_camera(self):
        """Test enabling a camera."""
        response = client.post("/surveillance/cameras/3/enable")
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_id"] == 3
        assert data["is_enabled"] == True
    
    def test_disable_camera(self):
        """Test disabling a camera."""
        response = client.post("/surveillance/cameras/1/disable")
        assert response.status_code == 200
        
        data = response.json()
        assert data["camera_id"] == 1
        assert data["is_enabled"] == False


class TestThumbnails:
    """Test thumbnail retrieval."""
    
    def test_get_camera_thumbnails(self):
        """Test getting camera thumbnails."""
        response = client.get("/surveillance/cameras/1/thumbnails")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            thumbnail = data[0]
            required_fields = ["id", "camera_id", "captured_at", "image_url"]
            for field in required_fields:
                assert field in thumbnail


class TestSensors:
    """Test sensor management endpoints."""
    
    def test_list_all_sensors(self):
        """Test listing all sensors."""
        response = client.get("/surveillance/sensors")
        assert response.status_code == 200
        
        data = response.json()
        assert "sensors" in data
        assert len(data["sensors"]) > 0
        
        # Check sensor structure
        sensor = data["sensors"][0]
        required_fields = ["sensor_id", "sensor_type", "is_armed", "is_triggered", "location"]
        for field in required_fields:
            assert field in sensor
    
    def test_arm_motion_detector(self):
        """Test arming motion detector."""
        response = client.post("/surveillance/sensors/motion/1/arm")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sensor_id"] == 1
        assert data["sensor_type"] == "motion"
        assert data["is_armed"] == True
    
    def test_disarm_motion_detector(self):
        """Test disarming motion detector."""
        response = client.post("/surveillance/sensors/motion/1/disarm")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sensor_id"] == 1
        assert data["sensor_type"] == "motion"
        assert data["is_armed"] == False
    
    def test_trigger_motion_detector(self):
        """Test triggering motion detector."""
        response = client.post("/surveillance/sensors/motion/1/trigger")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sensor_id"] == 1
        assert data["sensor_type"] == "motion"
        assert data["is_triggered"] == True
    
    def test_arm_windoor_sensor(self):
        """Test arming window/door sensor."""
        response = client.post("/surveillance/sensors/windoor/1/arm")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sensor_id"] == 1
        assert data["sensor_type"] == "windoor"
        assert data["is_armed"] == True
    
    def test_open_windoor_sensor(self):
        """Test opening window/door sensor."""
        response = client.post("/surveillance/sensors/windoor/1/open")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sensor_id"] == 1
        assert data["sensor_type"] == "windoor"
        assert data["is_opened"] == True
    
    def test_get_sensor_status_motion(self):
        """Test getting motion sensor detailed status."""
        response = client.get("/surveillance/sensors/motion/1/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sensor_id"] == 1
        assert data["sensor_type"] == "motion"
        assert "location" in data
        assert "is_armed" in data
        assert "is_triggered" in data
        assert "reading" in data
    
    def test_get_sensor_status_windoor(self):
        """Test getting window/door sensor detailed status."""
        response = client.get("/surveillance/sensors/windoor/1/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["sensor_id"] == 1
        assert data["sensor_type"] == "windoor"
        assert "location" in data
        assert "is_armed" in data
        assert "is_opened" in data
        assert "reading" in data
    
    def test_sensor_not_found(self):
        """Test accessing non-existent sensor."""
        response = client.post("/surveillance/sensors/motion/999/arm")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_invalid_sensor_type(self):
        """Test invalid sensor type."""
        response = client.get("/surveillance/sensors/invalid/1/status")
        assert response.status_code == 400
        assert "Invalid sensor type" in response.json()["detail"]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_camera_not_found_endpoints(self):
        """Test camera not found error handling."""
        endpoints = [
            ("/surveillance/cameras/999/view", "get"),
            ("/surveillance/cameras/999/ptz", "post", {"pan": 1}),
            ("/surveillance/cameras/999/password", "put", {"password": "test"}),
            ("/surveillance/cameras/999/password", "delete"),
            ("/surveillance/cameras/999/enable", "post"),
            ("/surveillance/cameras/999/disable", "post"),
            ("/surveillance/cameras/999/thumbnails", "get"),
        ]
        
        for endpoint_data in endpoints:
            url = endpoint_data[0]
            method = endpoint_data[1]
            payload = endpoint_data[2] if len(endpoint_data) > 2 else None
            
            if method == "get":
                response = client.get(url)
            elif method == "post":
                response = client.post(url, json=payload)
            elif method == "put":
                response = client.put(url, json=payload)
            elif method == "delete":
                response = client.delete(url)
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
