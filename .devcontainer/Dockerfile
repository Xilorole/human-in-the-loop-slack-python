FROM mcr.microsoft.com/vscode/devcontainers/base:bookworm

# Install uv
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN cp /root/.local/bin/uv /usr/local/bin/uv