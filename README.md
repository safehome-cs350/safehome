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

## Contact

- Sihun Chae: <csh1943@kaist.ac.kr>
- Wooyoung Choi: <wooyoung.choi@kaist.ac.kr>
- Donggeun Kim: <kdg01723@kaist.ac.kr>
