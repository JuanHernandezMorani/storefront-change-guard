"""Project path helpers with no dependency on the current working directory."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the repository root based on this module's location."""
    return Path(__file__).resolve().parents[2]
