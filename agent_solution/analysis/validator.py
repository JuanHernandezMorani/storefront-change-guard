"""Output validator for model results.

Validates every model result deterministically after parsing.
Returns validated result or MODEL_OUTPUT_INVALID with deterministic
failure explanation.
"""

from __future__ import annotations

import json
from typing import Any

from agent_solution.analysis.models import (
    AnalysisFinding,
    AnalysisMode,
    AnalysisStatus,
    Claim,
    ClaimStatus,
    EvidenceBundle,
    GroundedAnalysisResult,
    Severity,
)

_VALID_CLAIM_STATUSES = {s.value for s in ClaimStatus}
_VALID_SEVERITIES = {s.value for s in Severity}
_VALID_ANALYSIS_MODES = {m.value for m in AnalysisMode}


def _validate_json_object(raw: str) -> tuple[dict[str, Any] | None, str]:
    """Parse and validate JSON object from raw output.

    Handles markdown-wrapped JSON by extracting the first JSON object.
    """
    text = raw.strip()

    # Try direct parse first
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj, ""
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code block
    if "```" in text:
        # Find first code block
        start = text.find("```")
        if start >= 0:
            # Skip the opening ```
            after_open = text[start + 3:]
            # Find the language marker or newline
            newline = after_open.find("\n")
            if newline >= 0:
                content_start = start + 3 + newline + 1
            else:
                content_start = start + 3

            # Find closing ```
            end = text.find("```", content_start)
            if end > content_start:
                json_text = text[content_start:end].strip()
                try:
                    obj = json.loads(json_text)
                    if isinstance(obj, dict):
                        return obj, ""
                except json.JSONDecodeError:
                    pass

    # Try to find first { ... } block
    brace_start = text.find("{")
    if brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    json_text = text[brace_start : i + 1]
                    try:
                        obj = json.loads(json_text)
                        if isinstance(obj, dict):
                            return obj, ""
                    except json.JSONDecodeError:
                        pass
                    break

    return None, "Failed to parse JSON object from model output"


def _validate_top_level_fields(obj: dict[str, Any]) -> list[str]:
    """Validate required top-level fields."""
    errors: list[str] = []

    required_fields = ["analysis_mode", "summary", "claims", "findings"]
    for field in required_fields:
        if field not in obj:
            errors.append(f"Missing required field: {field}")

    return errors


def _validate_analysis_mode(obj: dict[str, Any]) -> list[str]:
    """Validate analysis_mode enum value."""
    mode = obj.get("analysis_mode", "")
    if mode not in _VALID_ANALYSIS_MODES:
        return [f"Invalid analysis_mode: {mode}"]
    return []


def _validate_claims(
    obj: dict[str, Any],
    evidence_bundle: EvidenceBundle,
) -> list[str]:
    """Validate claims array."""
    errors: list[str] = []
    claims = obj.get("claims", [])

    if not isinstance(claims, list):
        errors.append("claims must be a list")
        return errors

    valid_evidence_ids = {r.evidence_id for r in evidence_bundle.evidence_records}

    for i, claim in enumerate(claims):
        prefix = f"claims[{i}]"

        if not isinstance(claim, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        # Required fields
        for field in ["claim_id", "text", "claim_status"]:
            if field not in claim:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Claim status validation
        status = claim.get("claim_status", "")
        if status not in _VALID_CLAIM_STATUSES:
            errors.append(f"{prefix}: invalid claim_status '{status}'")
            continue

        # Evidence ID validation
        evidence_ids = claim.get("evidence_ids", [])
        if not isinstance(evidence_ids, list):
            errors.append(f"{prefix}: evidence_ids must be a list")
            continue

        for eid in evidence_ids:
            if eid not in valid_evidence_ids:
                errors.append(f"{prefix}: unknown evidence_id '{eid}'")

        # VERIFIED claims must have evidence
        if status == ClaimStatus.VERIFIED.value:
            if not evidence_ids:
                errors.append(f"{prefix}: VERIFIED claim must have evidence_ids")

        # INFERRED claims must have inference_basis and limitations
        if status == ClaimStatus.INFERRED.value:
            if not claim.get("inference_basis"):
                errors.append(f"{prefix}: INFERRED claim must have inference_basis")
            if not claim.get("limitations"):
                errors.append(f"{prefix}: INFERRED claim must have limitations")

        # UNKNOWN claims must not present unsupported factual conclusions
        if status == ClaimStatus.UNKNOWN.value:
            text = claim.get("text", "")
            # Check for factual claims in UNKNOWN status
            factual_indicators = ["is ", "are ", "was ", "has ", "does "]
            if any(indicator in text.lower() for indicator in factual_indicators):
                if "missing" not in text.lower() and "unknown" not in text.lower():
                    errors.append(
                        f"{prefix}: UNKNOWN claim should not present "
                        "unsupported factual conclusions"
                    )

        # OUT_OF_SCOPE claims must state authority boundary
        if status == ClaimStatus.OUT_OF_SCOPE.value:
            text = claim.get("text", "")
            if "phase" not in text.lower() and "scope" not in text.lower():
                errors.append(
                    f"{prefix}: OUT_OF_SCOPE claim must state authority boundary"
                )

    return errors


def _validate_findings(
    obj: dict[str, Any],
    valid_claim_ids: set[str],
) -> list[str]:
    """Validate findings array."""
    errors: list[str] = []
    findings = obj.get("findings", [])

    if not isinstance(findings, list):
        errors.append("findings must be a list")
        return errors

    for i, finding in enumerate(findings):
        prefix = f"findings[{i}]"

        if not isinstance(finding, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        # Required fields
        for field in ["title", "severity"]:
            if field not in finding:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Severity validation
        severity = finding.get("severity", "")
        if severity not in _VALID_SEVERITIES:
            errors.append(f"{prefix}: invalid severity '{severity}'")
            continue

        # Claim IDs validation
        claim_ids = finding.get("claim_ids", [])
        if not isinstance(claim_ids, list):
            errors.append(f"{prefix}: claim_ids must be a list")
            continue

        for cid in claim_ids:
            if cid not in valid_claim_ids:
                errors.append(f"{prefix}: unknown claim_id '{cid}'")

        # CRITICAL and HIGH findings must have VERIFIED supporting claims
        if severity in (Severity.CRITICAL.value, Severity.HIGH.value):
            if not claim_ids:
                errors.append(
                    f"{prefix}: {severity} finding must have at least one claim_id"
                )

    return errors


def _validate_phase_authority(
    obj: dict[str, Any],
) -> list[str]:
    """Validate phase authority constraints."""
    errors: list[str] = []
    mode = obj.get("analysis_mode", "")

    # PATCH_PROPOSAL must not authorize mutation
    if mode == AnalysisMode.PATCH_PROPOSAL.value:
        summary = obj.get("summary", "")
        if any(
            word in summary.lower()
            for word in ["apply patch", "execute change", "modify file", "write file"]
        ):
            errors.append("PATCH_PROPOSAL must not authorize direct mutation")

    # READINESS_ASSESSMENT must not declare final readiness
    if mode == AnalysisMode.READINESS_ASSESSMENT.value:
        summary = obj.get("summary", "")
        if any(
            phrase in summary.lower()
            for phrase in ["production ready", "approved for deployment", "ship it"]
        ):
            errors.append("READINESS_ASSESSMENT must not declare final production readiness")

    return errors


def validate_model_output(
    raw_output: str,
    evidence_bundle: EvidenceBundle,
    analysis_mode: AnalysisMode,
) -> GroundedAnalysisResult | tuple[None, str, list[str]]:
    """Validate raw model output against the structured schema.

    Returns GroundedAnalysisResult on success, or (None, status, errors) on failure.
    """
    # Step 1: Parse JSON
    obj, parse_error = _validate_json_object(raw_output)
    if obj is None:
        return (
            None,
            AnalysisStatus.MODEL_OUTPUT_INVALID.value,
            [parse_error],
        )

    all_errors: list[str] = []

    # Step 2: Validate top-level fields
    all_errors.extend(_validate_top_level_fields(obj))

    # Step 3: Validate analysis mode
    all_errors.extend(_validate_analysis_mode(obj))

    # Step 4: Validate claims
    all_errors.extend(_validate_claims(obj, evidence_bundle))

    # Step 5: Validate findings
    valid_claim_ids = {c.get("claim_id", "") for c in obj.get("claims", []) if isinstance(c, dict)}
    all_errors.extend(_validate_findings(obj, valid_claim_ids))

    # Step 6: Validate phase authority
    all_errors.extend(_validate_phase_authority(obj))

    # Step 7: Check for errors
    if all_errors:
        return (
            None,
            AnalysisStatus.MODEL_OUTPUT_INVALID.value,
            all_errors,
        )

    # Build validated result
    claims = []
    for c in obj.get("claims", []):
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
    for f in obj.get("findings", []):
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

    return GroundedAnalysisResult(
        analysis_request_id="",
        intake_request_id="",
        status=AnalysisStatus.ANALYSIS_COMPLETED,
        analysis_mode=AnalysisMode(obj["analysis_mode"]),
        summary=obj.get("summary", ""),
        claims=tuple(claims),
        findings=tuple(findings),
        next_safe_action=obj.get("next_safe_action", ""),
        phase_limitations=tuple(obj.get("phase_limitations", [])),
        evidence_bundle_sha256=evidence_bundle.bundle_sha256,
    )
