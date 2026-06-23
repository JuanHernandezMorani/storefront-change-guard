"""Placeholder domain models for the forthcoming review workflow.

Concrete schemas will be introduced only after the storefront baseline and output
contract are validated in the next phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ReadinessDecision(StrEnum):
    READY = "READY"
    READY_WITH_NOTES = "READY_WITH_NOTES"
    NEEDS_CHANGES = "NEEDS_CHANGES"
    BLOCKED = "BLOCKED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Normalized result for controlled command execution."""

    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
