"""Runtime configuration contracts.

Environment loading will be introduced when the local-model integration phase starts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    repository_path: Path
    artifacts_dir: Path
    policy_path: Path
    worktree_root: Path
