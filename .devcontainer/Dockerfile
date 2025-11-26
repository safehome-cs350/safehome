FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    xvfb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml ./

RUN pip install --no-cache-dir -e .

COPY . .

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown -R $USERNAME:$USERNAME /workspace

USER $USERNAME
