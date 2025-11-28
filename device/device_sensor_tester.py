"""Abstract base class for sensor devices with testing capability."""

from abc import ABC, abstractmethod


class DeviceSensorTester(ABC):
    """Abstract base class for sensor devices with testing capability.

    This class manages a linked list of sensors and provides a GUI
    for testing sensor functionality.
    """

    safe_home_sensor_test = None
    safehome_sensor_test = None  # alias for compatibility
    head_windoor_sensor = None
    head_motion_detector = None
    new_id_sequence_windoor_sensor = 0
    new_id_sequence_motion_detector = 0

    # Legacy aliases for backward compatibility
    # These use mixedCase for compatibility with existing code
    safeHomeSensorTest = None  # noqa: N815
    head_WinDoorSensor = None  # noqa: N815
    head_MotionDetector = None  # noqa: N815
    newIdSequence_WinDoorSensor = 0  # noqa: N815
    newIdSequence_MotionDetector = 0  # noqa: N815

    def __init__(self):
        """Initialize the sensor tester base class."""
        self.next = None
        self.next_sensor = None  # alias
        self.sensor_id = 0  # alias

    @abstractmethod
    def intrude(self):
        """Simulate intrusion/detection."""
        pass

    @abstractmethod
    def release(self):
        """Release intrusion/detection state."""
        pass

    @staticmethod
    def show_sensor_tester():
        """Show the sensor tester GUI."""
        if DeviceSensorTester.safe_home_sensor_test is not None:
            return
        try:
            import os

            if os.environ.get("SAFEHOME_HEADLESS") == "1":
                return
            import tkinter as tk

            from .safehome_sensor_test_gui import SafeHomeSensorTest

            root = tk._default_root
            if root is None:
                root = tk.Tk()
                root.withdraw()
            gui = SafeHomeSensorTest(master=root)
            # Mirror Java setVisible(true)
            try:
                gui.deiconify()
                gui.lift()
            except Exception:
                pass
            DeviceSensorTester.safe_home_sensor_test = gui
            DeviceSensorTester.safehome_sensor_test = gui
            # Legacy aliases
            DeviceSensorTester.safeHomeSensorTest = gui
        except Exception:
            # Fail silently in environments without display/Tkinter
            DeviceSensorTester.safe_home_sensor_test = None
            DeviceSensorTester.safehome_sensor_test = None
            DeviceSensorTester.safeHomeSensorTest = None

    # Legacy alias
    showSensorTester = show_sensor_tester  # noqa: N815
