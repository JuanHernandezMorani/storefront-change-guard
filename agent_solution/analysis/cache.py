"""Analysis cache backed by SQLite.

Provides deterministic cache key computation and cache invalidation
based on repository fingerprint.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from agent_solution.analysis.models import AnalysisCacheKey, GroundedAnalysisResult


def _compute_cache_key(key: AnalysisCacheKey) -> str:
    """Compute deterministic cache key hash."""
    parts = [
        key.normalized_request_sha256,
        key.task_type,
        key.output_language,
        key.model_id,
        key.runtime_profile_version,
        key.prompt_schema_version,
        key.repository_fingerprint,
        key.evidence_bundle_sha256,
        key.claim_policy_version,
    ]
    combined = "|".join(parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


class AnalysisCache:
    """SQLite-backed analysis cache."""

    def __init__(self, state_dir: Path):
        self._state_dir = state_dir
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = state_dir / "analysis_cache.db"
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    cache_key TEXT PRIMARY KEY,
                    normalized_request_sha256 TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    output_language TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    runtime_profile_version TEXT NOT NULL,
                    prompt_schema_version TEXT NOT NULL,
                    repository_fingerprint TEXT NOT NULL,
                    evidence_bundle_sha256 TEXT NOT NULL,
                    claim_policy_version TEXT NOT NULL,
                    analysis_result_json TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    last_accessed_at_utc TEXT NOT NULL
                )
            """)

    def get(
        self,
        key: AnalysisCacheKey,
        repository_fingerprint_complete: bool,
    ) -> GroundedAnalysisResult | None:
        """Retrieve cached result if valid.

        Returns None on cache miss or when fingerprint is incomplete.
        """
        if not repository_fingerprint_complete:
            return None

        cache_key = _compute_cache_key(key)

        with sqlite3.connect(str(self._db_path)) as conn:
            cursor = conn.execute(
                "SELECT analysis_result_json FROM analysis_cache WHERE cache_key = ?",
                (cache_key,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            # Update last accessed time
            now = datetime.now(UTC).isoformat()
            conn.execute(
                "UPDATE analysis_cache SET last_accessed_at_utc = ? WHERE cache_key = ?",
                (now, cache_key),
            )

            # Parse cached result
            try:
                result_dict = json.loads(row[0])
                return self._dict_to_result(result_dict)
            except (json.JSONDecodeError, KeyError):
                return None

    def put(
        self,
        key: AnalysisCacheKey,
        result: GroundedAnalysisResult,
        repository_fingerprint_complete: bool,
    ) -> bool:
        """Store result in cache.

        Returns True on success, False when fingerprint is incomplete.
        """
        if not repository_fingerprint_complete:
            return False

        cache_key = _compute_cache_key(key)
        now = datetime.now(UTC).isoformat()

        result_dict = {
            "analysis_request_id": result.analysis_request_id,
            "intake_request_id": result.intake_request_id,
            "status": result.status.value,
            "analysis_mode": result.analysis_mode.value,
            "summary": result.summary,
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "text": c.text,
                    "claim_status": c.claim_status.value,
                    "evidence_ids": list(c.evidence_ids),
                    "inference_basis": c.inference_basis,
                    "limitations": list(c.limitations),
                }
                for c in result.claims
            ],
            "findings": [
                {
                    "title": f.title,
                    "severity": f.severity.value,
                    "claim_ids": list(f.claim_ids),
                    "description": f.description,
                    "impact": f.impact,
                    "recommendation": f.recommendation,
                    "limitations": list(f.limitations),
                }
                for f in result.findings
            ],
            "recommendations": [
                {
                    "action": r.action,
                    "rationale": r.rationale,
                    "evidence_ids": list(r.evidence_ids),
                }
                for r in result.recommendations
            ],
            "next_safe_action": result.next_safe_action,
            "phase_limitations": list(result.phase_limitations),
            "evidence_bundle_sha256": result.evidence_bundle_sha256,
            "model_id": result.model_id,
            "runtime_profile_version": result.runtime_profile_version,
            "prompt_schema_version": result.prompt_schema_version,
            "cache_hit": result.cache_hit,
            "output_language": result.output_language,
            "created_at_utc": result.created_at_utc,
        }

        result_json = json.dumps(result_dict, ensure_ascii=False)

        with sqlite3.connect(str(self._db_path)) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO analysis_cache
                   (cache_key, normalized_request_sha256, task_type, output_language,
                    model_id, runtime_profile_version, prompt_schema_version,
                    repository_fingerprint, evidence_bundle_sha256, claim_policy_version,
                    analysis_result_json, created_at_utc, last_accessed_at_utc)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cache_key,
                    key.normalized_request_sha256,
                    key.task_type,
                    key.output_language,
                    key.model_id,
                    key.runtime_profile_version,
                    key.prompt_schema_version,
                    key.repository_fingerprint,
                    key.evidence_bundle_sha256,
                    key.claim_policy_version,
                    result_json,
                    now,
                    now,
                ),
            )

        return True

    def invalidate(self, repository_fingerprint: str) -> int:
        """Invalidate all cache entries for a given repository fingerprint.

        Returns the number of entries invalidated.
        """
        with sqlite3.connect(str(self._db_path)) as conn:
            cursor = conn.execute(
                "DELETE FROM analysis_cache WHERE repository_fingerprint = ?",
                (repository_fingerprint,),
            )
            return cursor.rowcount

    def clear(self) -> int:
        """Clear all cache entries.

        Returns the number of entries cleared.
        """
        with sqlite3.connect(str(self._db_path)) as conn:
            cursor = conn.execute("DELETE FROM analysis_cache")
            return cursor.rowcount

    def _dict_to_result(self, d: dict) -> GroundedAnalysisResult:
        """Convert dict back to GroundedAnalysisResult."""
        from agent_solution.analysis.models import (
            AnalysisFinding,
            AnalysisMode,
            AnalysisRecommendation,
            AnalysisStatus,
            Claim,
            ClaimStatus,
            Severity,
        )

        claims = []
        for c in d.get("claims", []):
            claims.append(
                Claim(
                    claim_id=c["claim_id"],
                    text=c["text"],
                    claim_status=ClaimStatus(c["claim_status"]),
                    evidence_ids=tuple(c.get("evidence_ids", [])),
                    inference_basis=c.get("inference_basis"),
                    limitations=tuple(c.get("limitations", [])),
                )
            )

        findings = []
        for f in d.get("findings", []):
            findings.append(
                AnalysisFinding(
                    title=f["title"],
                    severity=Severity(f["severity"]),
                    claim_ids=tuple(f.get("claim_ids", [])),
                    description=f.get("description", ""),
                    impact=f.get("impact", ""),
                    recommendation=f.get("recommendation", ""),
                    limitations=tuple(f.get("limitations", [])),
                )
            )

        recommendations = []
        for r in d.get("recommendations", []):
            recommendations.append(
                AnalysisRecommendation(
                    action=r["action"],
                    rationale=r.get("rationale", ""),
                    evidence_ids=tuple(r.get("evidence_ids", [])),
                )
            )

        return GroundedAnalysisResult(
            analysis_request_id=d.get("analysis_request_id", ""),
            intake_request_id=d.get("intake_request_id", ""),
            status=AnalysisStatus(d["status"]),
            analysis_mode=AnalysisMode(d["analysis_mode"]),
            summary=d.get("summary", ""),
            claims=tuple(claims),
            findings=tuple(findings),
            recommendations=tuple(recommendations),
            next_safe_action=d.get("next_safe_action", ""),
            phase_limitations=tuple(d.get("phase_limitations", [])),
            evidence_bundle_sha256=d.get("evidence_bundle_sha256", ""),
            model_id=d.get("model_id", ""),
            runtime_profile_version=d.get("runtime_profile_version", ""),
            prompt_schema_version=d.get("prompt_schema_version", ""),
            cache_hit=d.get("cache_hit", False),
            output_language=d.get("output_language", "en"),
            created_at_utc=d.get("created_at_utc", ""),
        )
