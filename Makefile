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
