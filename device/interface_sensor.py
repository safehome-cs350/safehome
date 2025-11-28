"""Abstract interface for sensor devices."""

from abc import ABC, abstractmethod


class InterfaceSensor(ABC):
    """Abstract base class for sensor device interfaces."""

    @abstractmethod
    def get_id(self):
        """Get the sensor ID.

        Returns:
            int: The sensor identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def read(self):
        """Read the current sensor state.

        Returns:
            bool: True if sensor detects an event, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def arm(self):
        """Enable/arm the sensor."""
        raise NotImplementedError

    @abstractmethod
    def disarm(self):
        """Disable/disarm the sensor."""
        raise NotImplementedError

    @abstractmethod
    def test_armed_state(self):
        """Test if the sensor is currently armed.

        Returns:
            bool: True if sensor is armed, False otherwise.
        """
        raise NotImplementedError
