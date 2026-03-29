"""Configuration management for cli-web-codewiki."""

from __future__ import annotations

from pathlib import Path

APP_NAME = "cli-web-codewiki"
CONFIG_DIR = Path.home() / ".config" / APP_NAME


def ensure_config_dir() -> Path:
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR
