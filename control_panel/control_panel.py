"""Control panel."""

import tkinter as tk
from enum import Enum

import httpx

from .control_panel_abstract import DeviceControlPanelAbstract


class ControlPanelState(Enum):
    """Enumeration for control panel states."""

    IDLE = 0
    MASTER = 1
    GUEST = 2
    PASSWORD_CHANGE_CURRENT = 3
    PASSWORD_CHANGE_NEW = 4
    PASSWORD_CHANGE_RECONFIRM = 5
    LOCKED = 6
    POWERED_OFF = 7


class ControlPanel(DeviceControlPanelAbstract):
    """Concrete implementation for the control panel."""

    SERVER_URL = "http://localhost:8000"

    def __init__(self):
        """Initialize the control panel."""
        super().__init__()
        self.set_display_away(False)
        self.set_display_stay(True)
        self.set_display_not_ready(False)
        self.set_display_short_message1("System Ready")
        self.set_display_short_message2("Enter Code")
        self.set_powered_led(True)
        self.button_sequence = ""
        self.state = ControlPanelState.IDLE
        self.user_id = "homeowner1"
        self.new_password = ""
        self.fail_count = 0

    def handle_wrong_password(self):
        """Handle wrong password."""
        self.fail_count += 1
        if self.fail_count >= 3:
            self.state = ControlPanelState.LOCKED
            self.set_display_short_message1("System Locked")
            self.set_display_short_message2("")
            self.fail_count = 0
            self.after(60000, self.unlock)
        elif self.state == ControlPanelState.IDLE:
            self.set_display_short_message1("Login Failed")
            self.set_display_short_message2("Enter Code")
        elif self.state == ControlPanelState.PASSWORD_CHANGE_CURRENT:
            self.state = ControlPanelState.MASTER
            self.set_display_short_message1("Wrong Password")
            self.set_display_short_message2("Choose Action")

    def check_password(self):
        """Check the entered password sequence."""
        if len(self.button_sequence) == 4:
            url = f"{self.SERVER_URL}/control-panel-login/"
            payload = {
                "user_id": self.user_id,
                "password": self.button_sequence,
            }
            try:
                with httpx.Client(timeout=5) as client:
                    response = client.post(url, json=payload)
                    response.raise_for_status()
                    role = response.json()
                    if role == "master":
                        self.state = ControlPanelState.MASTER
                        self.set_display_short_message1("Master Login")
                        self.set_display_short_message2("Choose Action")
                        self.fail_count = 0
                    elif role == "guest":
                        self.state = ControlPanelState.GUEST
                        self.set_display_short_message1("Guest Login")
                        self.set_display_short_message2("Choose Action")
                        self.fail_count = 0
            except httpx.HTTPStatusError:
                self.handle_wrong_password()
            except httpx.RequestError:
                self.set_display_short_message1("Server Error")
                self.set_display_short_message2("Enter Code")
            finally:
                self.button_sequence = ""

    def unlock(self):
        """Unlock the system after lock period."""
        self.state = ControlPanelState.IDLE
        self.set_display_short_message1("System Ready")
        self.set_display_short_message2("Enter Code")

    def password_change_check_password(self):
        """Check the entered password sequence."""
        if len(self.button_sequence) == 4:
            url = f"{self.SERVER_URL}/control-panel-login/"
            payload = {
                "user_id": self.user_id,
                "password": self.button_sequence,
            }
            try:
                with httpx.Client(timeout=5) as client:
                    response = client.post(url, json=payload)
                    response.raise_for_status()
                    role = response.json()
                    if role == "master":
                        self.state = ControlPanelState.PASSWORD_CHANGE_NEW
                        self.set_display_short_message1("Change Password")
                        self.set_display_short_message2("Enter New Password")
                    else:
                        self.handle_wrong_password()
            except httpx.HTTPStatusError:
                self.handle_wrong_password()
            except httpx.RequestError:
                self.state = ControlPanelState.MASTER
                self.set_display_short_message1("Server Error")
                self.set_display_short_message2("Choose Action")
            finally:
                self.button_sequence = ""

    def password_change_new_password(self):
        """Get the new password sequence."""
        if len(self.button_sequence) == 4:
            self.state = ControlPanelState.PASSWORD_CHANGE_RECONFIRM
            self.new_password = self.button_sequence
            self.button_sequence = ""
            self.set_display_short_message1("Change Password")
            self.set_display_short_message2("Enter Password Again")

    def password_change_reconfirm_password(self):
        """Reconfirm password sequence."""
        if len(self.button_sequence) == 4:
            self.state = ControlPanelState.MASTER
            if self.button_sequence == self.new_password:
                url = "http://localhost:8000/config/"
                payload = {
                    "user_id": self.user_id,
                    "password1": None,
                    "password2": None,
                    "master_password": self.new_password,
                    "guest_password": None,
                    "delay_time": None,
                    "phone_number": None,
                }
                try:
                    with httpx.Client(timeout=5) as client:
                        response = client.post(url, json=payload)
                        response.raise_for_status()
                        self.state = ControlPanelState.MASTER
                        self.set_display_short_message1("Password Changed")
                        self.set_display_short_message2("Choose Action")
                except httpx.HTTPError:
                    self.state = ControlPanelState.MASTER
                    self.set_display_short_message1("Server Error")
                    self.set_display_short_message2("Choose Action")
            else:
                self.state = ControlPanelState.PASSWORD_CHANGE_NEW
                self.set_display_short_message1("Passwords Mismatch")
                self.set_display_short_message2("Enter New Password")
            self.button_sequence = ""

    def power_on(self):
        """Power on the system."""
        httpx.post(f"{self.SERVER_URL}/power-on/", json={"user_id": self.user_id})
        self.state = ControlPanelState.IDLE
        self.set_powered_led(True)
        self.set_display_away(False)
        self.set_display_stay(True)
        self.set_display_not_ready(False)
        self.set_display_short_message1("System Ready")
        self.set_display_short_message2("Enter Code")

    def power_off(self):
        """Power off the system."""
        httpx.post(f"{self.SERVER_URL}/power-off/", json={"user_id": self.user_id})
        self.state = ControlPanelState.POWERED_OFF
        self.set_armed_led(False)
        self.set_powered_led(False)
        self.set_display_away(False)
        self.set_display_stay(False)
        self.set_display_not_ready(True)
        self.set_display_short_message1("")
        self.set_display_short_message2("")

    def reset(self):
        """Reset the system."""
        self.power_off()
        self.power_on()
        self.set_display_short_message1("System Reset")
        self.set_display_short_message2("Enter Code")

    def arm(self):
        """Arm the system."""
        try:
            response = httpx.post(f"{self.SERVER_URL}/arm/?user_id={self.user_id}")
            response.raise_for_status()
            self.set_armed_led(True)
            self.set_display_away(True)
            self.set_display_stay(False)
            self.set_display_short_message1("System Armed")
            self.set_display_short_message2("Choose Action")
        except httpx.HTTPError:
            self.set_display_short_message1("Fail Arming")
            self.set_display_short_message2("Choose Action")

    def disarm(self):
        """Disarm the system."""
        try:
            response = httpx.post(f"{self.SERVER_URL}/disarm/?user_id={self.user_id}")
            response.raise_for_status()
            self.set_armed_led(False)
            self.set_display_away(False)
            self.set_display_stay(True)
            self.set_display_short_message1("System Disarmed")
            self.set_display_short_message2("Choose Action")
        except httpx.HTTPError:
            self.set_display_short_message1("Fail Disarming")
            self.set_display_short_message2("Choose Action")

    def panic(self):
        """Trigger panic alarm."""
        self.set_armed_led(True)
        self.set_display_short_message1("PANIC ALARM!")
        self.set_display_short_message2("Help on the way")

    def handle_number_input(self, number: str):
        """Handle number input."""
        self.button_sequence += number
        self.set_display_short_message2(f"Code: {self.button_sequence}")
        if self.state == ControlPanelState.IDLE:
            self.check_password()
        elif self.state == ControlPanelState.PASSWORD_CHANGE_CURRENT:
            self.password_change_check_password()
        elif self.state == ControlPanelState.PASSWORD_CHANGE_NEW:
            self.password_change_new_password()
        elif self.state == ControlPanelState.PASSWORD_CHANGE_RECONFIRM:
            self.password_change_reconfirm_password()

    def button1(self):
        """Handle button 1 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("1")
        elif self.state == ControlPanelState.POWERED_OFF:
            self.power_on()

    def button2(self):
        """Handle button 2 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("2")
        elif self.state == ControlPanelState.MASTER:
            self.power_off()

    def button3(self):
        """Handle button 3 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("3")
        elif self.state == ControlPanelState.MASTER:
            self.reset()

    def button4(self):
        """Handle button 4 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("4")
        elif self.state == ControlPanelState.MASTER:
            self.arm()

    def button5(self):
        """Handle button 5 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("5")
        elif self.state == ControlPanelState.MASTER:
            self.disarm()

    def button6(self):
        """Handle button 6 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("6")
        elif self.state == ControlPanelState.MASTER:
            self.state = ControlPanelState.PASSWORD_CHANGE_CURRENT
            self.button_sequence = ""
            self.set_display_short_message1("Change Password")
            self.set_display_short_message2("Enter Current Password")

    def button7(self):
        """Handle button 7 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("7")

    def button8(self):
        """Handle button 8 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("8")

    def button9(self):
        """Handle button 9 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("9")

    def button_star(self):
        """Handle button * press."""
        if self.state == ControlPanelState.POWERED_OFF:
            return
        self.panic()

    def button0(self):
        """Handle button 0 press."""
        if self.state == ControlPanelState.LOCKED:
            return
        if self.state in (
            ControlPanelState.IDLE,
            ControlPanelState.PASSWORD_CHANGE_CURRENT,
            ControlPanelState.PASSWORD_CHANGE_NEW,
            ControlPanelState.PASSWORD_CHANGE_RECONFIRM,
        ):
            self.handle_number_input("0")

    def button_sharp(self):
        """Handle button # press."""
        if self.state == ControlPanelState.LOCKED:
            return
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
    app = ControlPanel()
    app.mainloop()
