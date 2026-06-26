"""Conservative task-type classifier.

Uses keyword matching with bilingual support (English and Spanish).
When confidence is insufficient, returns UNKNOWN.
Extracts explicit file targets from request text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from agent_solution.intake.models import ConfidenceLevel, TaskType

# ---------------------------------------------------------------------------
# Explicit file target extraction
# ---------------------------------------------------------------------------

_FILE_TARGET_PATTERN: re.Pattern[str] = re.compile(
    r"(?:review|check|analyze|fix|explain|what does|qué hace)\s+"
    r"(\S+?\.py)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Keyword patterns (English + Spanish)
# ---------------------------------------------------------------------------

_REVIEW_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\breview\b", re.IGNORECASE),
    re.compile(r"\bcheck\b.*\bchange\b", re.IGNORECASE),
    re.compile(r"\breview\b.*\bdiff\b", re.IGNORECASE),
    re.compile(r"\breview\b.*\bcurrent\b", re.IGNORECASE),
    re.compile(r"\brevis[áa]\b", re.IGNORECASE),
    re.compile(r"\brevisar\b", re.IGNORECASE),
    re.compile(r"\banalizar\b.*\bcambio\b", re.IGNORECASE),
    re.compile(r"\bhac[ée] una revis[io]?[áaó]?n?\b", re.IGNORECASE),
]

_BUG_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bfix\b.*\bbug\b", re.IGNORECASE),
    re.compile(r"\bfix\b.*\berror\b", re.IGNORECASE),
    re.compile(r"\bbug(s)?\b", re.IGNORECASE),
    re.compile(r"\berror\b", re.IGNORECASE),
    re.compile(r"\bcrash\b", re.IGNORECASE),
    re.compile(r"\bfailure\b", re.IGNORECASE),
    re.compile(r"\bregression\b", re.IGNORECASE),
    re.compile(r"\bfix\b.*\barregl[áa]\b", re.IGNORECASE),
    re.compile(r"\bbug\b.*\barregl[áa]\b", re.IGNORECASE),
    re.compile(r"\barreglar\b", re.IGNORECASE),
    re.compile(r"\berror\b.*\bfix\b", re.IGNORECASE),
    re.compile(r"\bfind\b.*\bdefect(s|o)?\b", re.IGNORECASE),
    re.compile(r"\bidentify\b.*\bdefect(s|o)?\b", re.IGNORECASE),
    re.compile(r"\bencontr[áa]?\b.*\bdefect(s|o)?\b", re.IGNORECASE),
    re.compile(r"\bencontrar\b.*\bdefect(s|o)?\b", re.IGNORECASE),
]

_CODEBASE_Q_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bexplain\b", re.IGNORECASE),
    re.compile(r"\bhow\b.*\b(work|does|calculated|computed|built)\b", re.IGNORECASE),
    re.compile(r"\bwhere\b.*\b(is|are|defined|located)\b", re.IGNORECASE),
    re.compile(r"\bwhat\b.*\b(is|are|does)\b", re.IGNORECASE),
    re.compile(r"\bcodebase\b", re.IGNORECASE),
    re.compile(r"\bexplainar?\b", re.IGNORECASE),
    re.compile(r"\bc[óo]mo\b.*\b(trabaja|funciona|calcula|opera)\b", re.IGNORECASE),
    re.compile(r"\bd[óo]nde\b.*\b(est[áa]|defin|ubic)\b", re.IGNORECASE),
    re.compile(r"\bqu[ée]\b.*\b(es|hace)\b", re.IGNORECASE),
    re.compile(r"\bwhat does\b.*\bdo\b", re.IGNORECASE),
    re.compile(r"\bqué hace\b.*\b\w+\b", re.IGNORECASE),
]

_READINESS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bready\b", re.IGNORECASE),
    re.compile(r"\bproduction\b", re.IGNORECASE),
    re.compile(r"\bdeployment\b", re.IGNORECASE),
    re.compile(r"\bshippable\b", re.IGNORECASE),
    re.compile(r"\bdeploy\b", re.IGNORECASE),
    re.compile(r"\blaunch\b", re.IGNORECASE),
    re.compile(r"\brelease\b", re.IGNORECASE),
    re.compile(r"\blisto\b", re.IGNORECASE),
    re.compile(r"\bproducci[óo]n\b", re.IGNORECASE),
    re.compile(r"\bdesplegar\b", re.IGNORECASE),
    re.compile(r"\bentregar\b", re.IGNORECASE),
]

_PATCH_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bpatch\b", re.IGNORECASE),
    re.compile(r"\bfix\s+it\b", re.IGNORECASE),
    re.compile(r"\bchange\b.*\bcode\b", re.IGNORECASE),
    re.compile(r"\bedit\b.*\bcode\b", re.IGNORECASE),
    re.compile(r"\bmodify\b", re.IGNORECASE),
    re.compile(r"\bimprove\b", re.IGNORECASE),
    re.compile(r"\brefactor\b", re.IGNORECASE),
    re.compile(r"\boptimize\b", re.IGNORECASE),
    re.compile(r"\bbetter\b", re.IGNORECASE),
    re.compile(r"\bapply\b.*\bpatch\b", re.IGNORECASE),
    re.compile(r"\bcorregir\b", re.IGNORECASE),
    re.compile(r"\bmodificar\b", re.IGNORECASE),
    re.compile(r"\bmejorar\b", re.IGNORECASE),
    re.compile(r"\brefactorizar\b", re.IGNORECASE),
    re.compile(r"\bvalidate\b.*\bwith\b", re.IGNORECASE),
    re.compile(r"\bvalidation\b.*\bcommand\b", re.IGNORECASE),
    re.compile(r"\bexpected\b.*:", re.IGNORECASE),
    re.compile(r"\bshould\b.*\bresult\b", re.IGNORECASE),
    re.compile(r"\bvalidar\b.*\bcon\b", re.IGNORECASE),
    re.compile(r"\besperado\b.*:", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class _MatchResult:
    task_type: TaskType
    score: int
    confidence: ConfidenceLevel


def _count_matches(text: str, patterns: list[re.Pattern[str]]) -> int:
    total = 0
    for pat in patterns:
        if pat.search(text):
            total += 1
    return total


def classify_request(text: str) -> tuple[TaskType, ConfidenceLevel]:
    """Classify an incoming request into a task type.

    Returns the detected type and a confidence level.  When no type
    achieves sufficient confidence, returns (UNKNOWN, LOW).
    """
    scores: list[_MatchResult] = []

    for task_type, patterns in [
        (TaskType.CODE_REVIEW, _REVIEW_PATTERNS),
        (TaskType.BUG_DIAGNOSIS, _BUG_PATTERNS),
        (TaskType.CODEBASE_QUESTION, _CODEBASE_Q_PATTERNS),
        (TaskType.READINESS_ASSESSMENT, _READINESS_PATTERNS),
        (TaskType.PATCH_PROPOSAL, _PATCH_PATTERNS),
    ]:
        score = _count_matches(text, patterns)
        if score == 0:
            continue
        if score >= 3:
            conf = ConfidenceLevel.HIGH
        elif score >= 2:
            conf = ConfidenceLevel.MEDIUM
        else:
            conf = ConfidenceLevel.LOW
        scores.append(_MatchResult(task_type=task_type, score=score, confidence=conf))

    if not scores:
        return TaskType.UNKNOWN, ConfidenceLevel.LOW

    scores.sort(key=lambda m: m.score, reverse=True)
    best = scores[0]

    if best.confidence == ConfidenceLevel.LOW and len(scores) > 1:
        second = scores[1]
        if second.score == best.score:
            return TaskType.UNKNOWN, ConfidenceLevel.LOW

    return best.task_type, best.confidence


def extract_file_targets(text: str) -> tuple[str, ...]:
    """Extract explicit file targets from request text.

    Returns a tuple of file paths found in the request.
    Only extracts .py files for now (conservative approach).
    """
    matches = _FILE_TARGET_PATTERN.findall(text)
    return tuple(matches)
