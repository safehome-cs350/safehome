"""Window/Door sensor device implementation."""

from .device_sensor_tester import DeviceSensorTester
from .interface_sensor import InterfaceSensor


class DeviceWinDoorSensor(DeviceSensorTester, InterfaceSensor):
    """Window/Door sensor device.

    This sensor detects when windows or doors are opened/closed.
    """

    def __init__(self):
        """Initialize the Window/Door sensor device."""
        super().__init__()

        # Assign unique ID
        DeviceSensorTester.new_id_sequence_windoor_sensor += 1
        DeviceSensorTester.newIdSequence_WinDoorSensor = (
            DeviceSensorTester.new_id_sequence_windoor_sensor
        )
        self.sensor_id = DeviceSensorTester.new_id_sequence_windoor_sensor

        # Initialize state
        self.opened = False
        self.armed = False

        # Add to linked list
        DeviceSensorTester.head_windoor_sensor = self
        DeviceSensorTester.head_WinDoorSensor = self  # legacy alias
        self.next = DeviceSensorTester.head_windoor_sensor
        self.next_sensor = self.next  # alias

        # Update GUI and link heads
        gui = DeviceSensorTester.safe_home_sensor_test
        if gui is None:
            gui = DeviceSensorTester.safeHomeSensorTest
        if gui is not None:
            gui.head_windoor = DeviceSensorTester.head_windoor_sensor
            range_var = getattr(gui, "rangeSensorID_WinDoorSensor", None) or getattr(
                gui, "range_sensor_id_windoor", None
            )
            if range_var is not None:
                range_var.set(
                    f"1 ~ {DeviceSensorTester.new_id_sequence_windoor_sensor}"
                )

    def intrude(self):
        """Simulate opening the window/door."""
        self.opened = True

    def release(self):
        """Simulate closing the window/door."""
        self.opened = False

    def get_id(self):
        """Alias for getID."""
        return self.sensor_id

    def read(self):
        """Read the sensor state."""
        if self.armed:
            return self.opened
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
