"""Result renderer for validated analysis results.

Deterministic rendering from validated structured results.
Never invents additional facts.
"""

from __future__ import annotations

from agent_solution.analysis.models import (
    AnalysisFinding,
    Claim,
    GroundedAnalysisResult,
)

# Spanish translations for common terms
_SPANISH_TRANSLATIONS: dict[str, str] = {
    "VERIFIED": "VERIFICADO",
    "INFERRED": "INFERIDO",
    "UNKNOWN": "DESCONOCIDO",
    "OUT_OF_SCOPE": "FUERA_DE_AMBITO",
    "CRITICAL": "CRITICO",
    "HIGH": "ALTO",
    "MEDIUM": "MEDIO",
    "LOW": "BAJO",
    "INFO": "INFORMACION",
    "ANALYSIS_COMPLETED": "ANALISIS_COMPLETADO",
    "ANALYSIS_CACHE_HIT": "ANALISIS_CACHE_HIT",
    "INTAKE_BLOCKED": "INTAKE_BLOQUEADO",
    "INSUFFICIENT_EVIDENCE": "EVIDENCIA_INSUFICIENTE",
    "MODEL_UNAVAILABLE": "MODELO_NO_DISPONIBLE",
    "MODEL_TIMEOUT": "MODELO_TIMEOUT",
    "MODEL_EXECUTION_FAILED": "FALLA_EJECUCION_MODELO",
    "MODEL_OUTPUT_INVALID": "SALIDA_MODELO_INVALIDA",
    "EVIDENCE_VALIDATION_FAILED": "VALIDACION_EVIDENCIA_FALLIDA",
    "PHASE_AUTHORITY_LIMIT": "LIMITE_AUTORIDAD_FASE",
}


def _translate(text: str, language: str) -> str:
    """Translate a term if language is Spanish."""
    if language == "es":
        return _SPANISH_TRANSLATIONS.get(text, text)
    return text


def _render_claim(claim: Claim, language: str) -> str:
    """Render a single claim."""
    status = _translate(claim.claim_status.value, language)
    lines = [f"  [{claim.claim_id}] ({status}) {claim.text}"]

    if claim.evidence_ids:
        lines.append(f"    Evidence: {', '.join(claim.evidence_ids)}")

    if claim.inference_basis:
        lines.append(f"    Basis: {claim.inference_basis}")

    if claim.limitations:
        for lim in claim.limitations:
            lines.append(f"    Limitation: {lim}")

    return "\n".join(lines)


def _render_finding(finding: AnalysisFinding, language: str) -> str:
    """Render a single finding."""
    severity = _translate(finding.severity.value, language)
    lines = [f"  [{severity}] {finding.title}"]

    if finding.claim_ids:
        lines.append(f"    Claims: {', '.join(finding.claim_ids)}")

    if finding.description:
        lines.append(f"    Description: {finding.description}")

    if finding.impact:
        lines.append(f"    Impact: {finding.impact}")

    if finding.recommendation:
        lines.append(f"    Recommendation: {finding.recommendation}")

    if finding.limitations:
        for lim in finding.limitations:
            lines.append(f"    Limitation: {lim}")

    return "\n".join(lines)


def render_text(result: GroundedAnalysisResult, language: str = "en") -> str:
    """Render analysis result as human-readable text."""
    sections: list[str] = []

    # Status
    status_text = _translate(result.status.value, language)
    sections.append(f"Status: {status_text}")

    # Cache hit indicator
    if result.cache_hit:
        sections.append("Source: Cache")

    # Summary
    sections.append(f"\nSummary:\n{result.summary}")

    # Claims
    if result.claims:
        sections.append("\nClaims:")
        for claim in result.claims:
            sections.append(_render_claim(claim, language))

    # Findings
    if result.findings:
        sections.append("\nFindings:")
        for finding in result.findings:
            sections.append(_render_finding(finding, language))

    # Next safe action
    if result.next_safe_action:
        sections.append(f"\nNext safe action: {result.next_safe_action}")

    # Phase limitations
    if result.phase_limitations:
        sections.append("\nLimitations:")
        for lim in result.phase_limitations:
            sections.append(f"  - {lim}")

    return "\n".join(sections)


def render_json(result: GroundedAnalysisResult) -> dict:
    """Render analysis result as JSON-serializable dict."""
    return {
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


def render_result(
    result: GroundedAnalysisResult,
    format: str = "text",
    language: str = "en",
) -> str | dict:
    """Render analysis result in the requested format."""
    if format == "json":
        return render_json(result)
    return render_text(result, language)
