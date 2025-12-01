# SafeHome User Manual - Team 5

## Prerequisites

1. Install Docker

    <https://docs.docker.com/engine/install/>

2. Install dependencies:

    ```sh
    pip install -e .
    ```

## Execution

There are **three** main components to run:

1. Server

    ```sh
    make backend
    ```

2. Web UI

    ```sh
    make frontend
    ```

3. Control Panel

    ```sh
    make control-panel
    ```

## Testing

You can check the coverage report along with the unit tests.
If you want to inspect detailed coverage results, run the unit tests first and then open the HTML report located in the htmlcov/ directory.

```sh
# Backend unit tests
make backend-unit-test

# Frontend unit tests
make frontend-unit-test

# Control panel unit tests
make control-panel-unit-test

# Integration tests
make integration-test
```

## How to use our safehome implementation through concrete examples of use case scenarios

Please refer to the integration test code in `/tests/integration_tests`.
There, you can see how every use case is executed end-to-end and how the backend, frontend, and control panel interact with each other during the full system workflow.

To illustrate the “Log onto the system through the control panel” use case, consider the following concrete example.

When the user enters a password on the control panel, the control panel sends a login request to the backend server:

```python
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
```

This snippet shows that the control panel constructs an HTTP POST request containing the user ID and the password entered via the number button. The request is then sent to the backend server.

On the backend side, the following endpoint handles this login request:

```python
@router.post(
    "/control-panel-login/",
    summary="UC1.a. Log onto the system through control panel.",
    responses={
        401: {
            "description": "Invalid user ID or password",
            "content": {
                "application/json": {
                    "example": {"detail": "string"},
                }
            },
        }
    },
)
def control_panel_login(request: ControlPanelLoginRequest):
    """UC1.a. Log onto the system through control panel."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="ID not recognized")

    if request.password == user.master_password:
        return "master"
    elif request.password == user.guest_password:
        return "guest"
    else:
        raise HTTPException(status_code=401, detail="Password incorrect")
```

The backend looks up the user, verifies the password, and returns either "master" or "guest" depending on which password matches. If the credentials are invalid, the server returns HTTP 401, triggering the Control Panel’s error-handling logic.

This demonstrates the complete flow of the “Log onto the system through control panel” use case:
user input → control panel request → backend authentication → control panel state update.

## Contact

- Sihun Chae: <csh1943@kaist.ac.kr>
- Wooyoung Choi: <wooyoung.choi@kaist.ac.kr>
- Donggeun Kim: <kdg01723@kaist.ac.kr>
