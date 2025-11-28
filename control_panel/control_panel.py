#!/usr/bin/env python3
"""Control Panel Example
=====================
This example demonstrates the SafeHome Control Panel GUI with:
- Number keypad (0-9, *, #)
- LED indicators (armed, power)
- Status displays (away, stay, not ready)
- Message display area

Usage:
    python -m example.example_control_panel
    OR
    python example_control_panel.py (when run from example directory)
"""

import sys
import tkinter as tk
from enum import Enum
from pathlib import Path

import httpx

# Add parent directory to path for direct script execution
if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))


from .control_panel_abstract import DeviceControlPanelAbstract


class ControlPanelState(Enum):
    """Enumeration for control panel states."""

    IDLE = 0
    MASTER = 1
    GUEST = 2


# Example implementation for testing
class TestControlPanel(DeviceControlPanelAbstract):
    """Concrete implementation for testing the control panel."""

    SERVER_URL = "http://localhost:8000"

    def __init__(self):
        """Initialize the control panel."""
        super().__init__()
        self.set_display_short_message1("System Ready")
        self.set_display_short_message2("Enter Code")
        self.set_powered_led(True)
        self.button_sequence = ""
        self.state = ControlPanelState.IDLE
        self.user_id = "homeowner1"

    def check_password(self):
        """Check the entered password sequence."""
        if len(self.button_sequence) == 4:
            url = "http://localhost:8000/control-panel-login/"
            payload = {"user_id": self.user_id, "password": self.button_sequence}
            try:
                with httpx.Client(timeout=5) as client:
                    response = client.post(url, json=payload)
                    response.raise_for_status()
                    role = response.json()
                    if role == "master":
                        self.state = ControlPanelState.MASTER
                        self.set_display_short_message1("Master Login")
                    elif role == "guest":
                        self.state = ControlPanelState.GUEST
                        self.set_display_short_message1("Guest Login")
            except httpx.HTTPStatusError:
                self.set_display_short_message1("Login Failed")
            except httpx.RequestError:
                self.set_display_short_message1("Server Error")
            finally:
                self.button_sequence = ""
                self.set_display_short_message2("Choose Action")

    def button1(self):
        """Handle button 1 press."""
        if self.state == ControlPanelState.IDLE:
            self.button_sequence += "1"
            self.set_display_short_message2(f"Code: {self.button_sequence}")
            self.check_password()
        elif self.state == ControlPanelState.MASTER:
            try:
                response = httpx.post(
                    f"{self.SERVER_URL}/power-on/", json={"user_id": self.user_id}
                )
                response.raise_for_status()
                self.set_powered_led(True)
                print("Power on")
            except httpx.HTTPError as e:
                print("Failed to power on:", e)

    def button2(self):
        """Handle button 2 press."""
        if self.state == ControlPanelState.IDLE:
            self.button_sequence += "2"
            self.set_display_short_message2(f"Code: {self.button_sequence}")
            self.check_password()
        elif self.state == ControlPanelState.MASTER:
            try:
                response = httpx.post(
                    f"{self.SERVER_URL}/power-off/", json={"user_id": self.user_id}
                )
                response.raise_for_status()
                self.set_powered_led(False)
                print("Power off")
            except httpx.HTTPError as e:
                print("Failed to power off:", e)

    def button3(self):
        """Handle button 3 press."""
        if self.state == ControlPanelState.IDLE:
            self.button_sequence += "3"
            self.set_display_short_message2(f"Code: {self.button_sequence}")
            self.check_password()
        elif self.state == ControlPanelState.MASTER:
            try:
                # Power off
                response = httpx.post(
                    f"{self.SERVER_URL}/power-off/", json={"user_id": self.user_id}
                )
                response.raise_for_status()
                self.set_powered_led(False)
                # Power on
                response = httpx.post(
                    f"{self.SERVER_URL}/power-on/", json={"user_id": self.user_id}
                )
                response.raise_for_status()
                self.set_powered_led(True)
                print("Reset")
            except httpx.HTTPError as e:
                print("Failed to reset:", e)

    def button4(self):
        print("Button 4 pressed")
        self.button_sequence += "4"
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        self.check_password()

    def button5(self):
        print("Button 5 pressed")
        self.button_sequence += "5"
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        self.check_password()

    def button6(self):
        print("Button 6 pressed")
        self.button_sequence += "6"
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        self.check_password()

    def button7(self):
        print("Button 7 pressed")
        self.button_sequence += "7"
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        self.check_password()

    def button8(self):
        print("Button 8 pressed")
        self.button_sequence += "8"
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        self.check_password()

    def button9(self):
        print("Button 9 pressed")
        self.button_sequence += "9"
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        self.check_password()

    def button_star(self):
        print("Button * pressed (Panic)")
        self.set_armed_led(True)
        self.set_display_short_message1("PANIC ALARM!")
        self.set_display_short_message2("Help on the way")

    def button0(self):
        print("Button 0 pressed")
        self.button_sequence += "0"
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        self.check_password()

    def button_sharp(self):
        print("Button # pressed (Reset/Panic)")
        # Reset sequence
        self.button_sequence = ""
        self.set_armed_led(False)
        self.set_display_away(False)
        self.set_display_stay(False)
        self.set_display_not_ready(False)
        self.set_display_short_message1("System Ready")
        self.set_display_short_message2("Enter Code")


if __name__ == "__main__":
    # Create root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Run the test control panel
    app = TestControlPanel()
    print("Control Panel GUI started")
    print("Try entering code 1-2-3 to arm the system")
    print("Press * for panic alarm")
    print("Press # to reset")
    app.mainloop()
