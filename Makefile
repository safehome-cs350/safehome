IMAGE_NAME = safehome:latest
WORKSPACE = $(shell pwd)

.PHONY: build
build:
	docker build -t $(IMAGE_NAME) -f .devcontainer/Dockerfile .

.PHONY: backend-unit-test
backend-unit-test: build
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		bash -c "coverage run --source=backend -m pytest backend/tests/unit_tests && \
		coverage xml -o backend-coverage.xml && \
		coverage report -m"

.PHONY: frontend-unit-test
frontend-unit-test: build
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		bash -c "xvfb-run -a coverage run --source=frontend -m pytest frontend/tests && \
		coverage xml -o frontend-coverage.xml && \
		coverage report -m"

.PHONY: control-panel-unit-test
control-panel-unit-test: build
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		bash -c "xvfb-run -a coverage run --source=control_panel -m pytest control_panel/tests/unit_tests -v && \
		coverage xml -o control-panel-coverage.xml && \
		coverage report -m"

.PHONY: integration-test
integration-test: build
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		bash -c "\
			uvicorn backend.app:app --host 0.0.0.0 --port 8000 --log-level warning --no-access-log & \
			SERVER_PID=\$$!; \
			until nc -z localhost 8000; do sleep 0.1; done; \
			xvfb-run -a pytest tests/integration_tests -v; \
			kill \$$SERVER_PID; \
			wait \$$SERVER_PID || true"

.PHONY: frontend
frontend:
	python3 -m frontend.main

.PHONY: backend
backend:
	docker compose up

.PHONY: control-panel
control-panel:
	python3 -m control_panel.control_panel
