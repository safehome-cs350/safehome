IMAGE_NAME = safehome:latest
WORKSPACE = $(shell pwd)

.PHONY: build
build:
	docker build -t $(IMAGE_NAME) -f .devcontainer/Dockerfile .

.PHONY: backend-unit-test
backend-unit-test: build
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		coverage run --source=backend -m pytest backend/tests/unit_tests
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		coverage xml -o backend-coverage.xml
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		coverage report -m

.PHONY: frontend-unit-test
frontend-unit-test: build
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		xvfb-run -a coverage run --source=frontend -m pytest frontend/tests
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		coverage xml -o frontend-coverage.xml
	docker run --rm -v $(WORKSPACE):/workspace -w /workspace $(IMAGE_NAME) \
		coverage report -m
