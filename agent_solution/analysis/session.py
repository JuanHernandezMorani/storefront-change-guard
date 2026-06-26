"""Compact session state store backed by SQLite.

Stores only compact structured state without raw conversation transcripts.
Session state must not override a fresh intake decision.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SessionState:
    """Compact session state."""

    session_id: str
    current_goal: str
    task_type: str
    repository_fingerprint: str
    completed_analysis_ids: tuple[str, ...] = ()
    evidence_reference_ids: tuple[str, ...] = ()
    unresolved_questions: tuple[str, ...] = ()
    known_limitations: tuple[str, ...] = ()
    last_safe_action: str = ""
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    updated_at_utc: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class SessionStateStore:
    """SQLite-backed compact session state store."""

    def __init__(self, state_dir: Path):
        self._state_dir = state_dir
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = state_dir / "session_state.db"
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    current_goal TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    repository_fingerprint TEXT NOT NULL,
                    completed_analysis_ids TEXT NOT NULL,
                    evidence_reference_ids TEXT NOT NULL,
                    unresolved_questions TEXT NOT NULL,
                    known_limitations TEXT NOT NULL,
                    last_safe_action TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                )
            """)

    def get(self, session_id: str) -> SessionState | None:
        """Retrieve session state by ID."""
        with sqlite3.connect(str(self._db_path)) as conn:
            cursor = conn.execute(
                "SELECT * FROM session_state WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return SessionState(
                session_id=row[0],
                current_goal=row[1],
                task_type=row[2],
                repository_fingerprint=row[3],
                completed_analysis_ids=tuple(json.loads(row[4])),
                evidence_reference_ids=tuple(json.loads(row[5])),
                unresolved_questions=tuple(json.loads(row[6])),
                known_limitations=tuple(json.loads(row[7])),
                last_safe_action=row[8],
                created_at_utc=row[9],
                updated_at_utc=row[10],
            )

    def create(
        self,
        current_goal: str,
        task_type: str,
        repository_fingerprint: str,
    ) -> SessionState:
        """Create a new session state."""
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()

        state = SessionState(
            session_id=session_id,
            current_goal=current_goal,
            task_type=task_type,
            repository_fingerprint=repository_fingerprint,
            created_at_utc=now,
            updated_at_utc=now,
        )

        self._save(state)
        return state

    def update(
        self,
        session_id: str,
        repository_fingerprint: str,
        **kwargs: str | tuple[str, ...],
    ) -> SessionState | None:
        """Update session state.

        Returns None if session not found or fingerprint doesn't match.
        Session state cannot override a changed repository fingerprint.
        """
        existing = self.get(session_id)
        if existing is None:
            return None

        # Check fingerprint - cannot override changed fingerprint
        if existing.repository_fingerprint != repository_fingerprint:
            return None

        now = datetime.now(UTC).isoformat()
        updated = SessionState(
            session_id=session_id,
            current_goal=kwargs.get("current_goal", existing.current_goal),
            task_type=kwargs.get("task_type", existing.task_type),
            repository_fingerprint=repository_fingerprint,
            completed_analysis_ids=kwargs.get(
                "completed_analysis_ids", existing.completed_analysis_ids
            ),
            evidence_reference_ids=kwargs.get(
                "evidence_reference_ids", existing.evidence_reference_ids
            ),
            unresolved_questions=kwargs.get(
                "unresolved_questions", existing.unresolved_questions
            ),
            known_limitations=kwargs.get(
                "known_limitations", existing.known_limitations
            ),
            last_safe_action=kwargs.get("last_safe_action", existing.last_safe_action),
            created_at_utc=existing.created_at_utc,
            updated_at_utc=now,
        )

        self._save(updated)
        return updated

    def delete(self, session_id: str) -> bool:
        """Delete session state."""
        with sqlite3.connect(str(self._db_path)) as conn:
            cursor = conn.execute(
                "DELETE FROM session_state WHERE session_id = ?",
                (session_id,),
            )
            return cursor.rowcount > 0

    def _save(self, state: SessionState) -> None:
        """Save session state to database."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO session_state
                   (session_id, current_goal, task_type, repository_fingerprint,
                    completed_analysis_ids, evidence_reference_ids,
                    unresolved_questions, known_limitations,
                    last_safe_action, created_at_utc, updated_at_utc)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    state.session_id,
                    state.current_goal,
                    state.task_type,
                    state.repository_fingerprint,
                    json.dumps(list(state.completed_analysis_ids)),
                    json.dumps(list(state.evidence_reference_ids)),
                    json.dumps(list(state.unresolved_questions)),
                    json.dumps(list(state.known_limitations)),
                    state.last_safe_action,
                    state.created_at_utc,
                    state.updated_at_utc,
                ),
            )

    def has_raw_transcript(self, session_id: str) -> bool:
        """Verify no raw transcript is stored.

        This is a contract verification method - always returns False
        for a correctly implemented store.
        """
        # By design, we never store raw transcripts
        return False
