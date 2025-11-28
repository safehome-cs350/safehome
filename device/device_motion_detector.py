"""Motion detector device implementation."""

from .device_sensor_tester import DeviceSensorTester
from .interface_sensor import InterfaceSensor


class DeviceMotionDetector(DeviceSensorTester, InterfaceSensor):
    """Motion detector device.

    This sensor detects motion in its detection area.
    """

    def __init__(self):
        """Initialize the Motion Detector device."""
        super().__init__()

        # Assign unique ID
        DeviceSensorTester.new_id_sequence_motion_detector += 1
        DeviceSensorTester.newIdSequence_MotionDetector = (
            DeviceSensorTester.new_id_sequence_motion_detector
        )
        self.sensor_id = DeviceSensorTester.new_id_sequence_motion_detector

        # Initialize state
        self.detected = False
        self.armed = False

        # Add to linked list
        DeviceSensorTester.head_motion_detector = self
        DeviceSensorTester.head_MotionDetector = self  # legacy alias
        self.next = DeviceSensorTester.head_motion_detector
        self.next_sensor = self.next  # alias

        # Update GUI and link heads
        gui = DeviceSensorTester.safe_home_sensor_test
        if gui is None:
            gui = DeviceSensorTester.safeHomeSensorTest
        if gui is not None:
            gui.head_motion = DeviceSensorTester.head_motion_detector
            range_var = getattr(gui, "rangeSensorID_MotionDetector", None) or getattr(
                gui, "range_sensor_id_motion", None
            )
            if range_var is not None:
                range_var.set(
                    f"1 ~ {DeviceSensorTester.new_id_sequence_motion_detector}"
                )

    def intrude(self):
        """Simulate motion detection."""
        self.detected = True

    def release(self):
        """Clear motion detection."""
        self.detected = False

    def get_id(self):
        """Alias for getID."""
        return self.sensor_id

    def read(self):
        """Read the sensor state."""
        if self.armed:
            return self.detected
        return False

    def arm(self):
        """Enable the sensor."""
        self.armed = True

    def disarm(self):
        """Disable the sensor."""
        self.armed = False

    def test_armed_state(self):
        """Test if the sensor is enabled."""
        return self.armed
