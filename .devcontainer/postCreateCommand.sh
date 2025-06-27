#!/bin/zsh

uv python pin "$(cat .python-version)"
uv sync --dev
# uv run jupyter --paths

# Install starship
echo "$(starship init zsh)" >> ~/.zshrc