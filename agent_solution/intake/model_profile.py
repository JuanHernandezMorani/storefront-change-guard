"""Model-profile contract for future routing.

Model-agnostic configuration that will later support routing decisions
based on benchmark results.  No final values are assumed.
"""

from __future__ import annotations

from agent_solution.intake.models import (
    CacheKey,
    ModelProfile,
    TaskType,
)

# ---------------------------------------------------------------------------
# Provisional profile templates
#
# These are structural templates only.  model_id, context_limit,
# budget, and timeout values are placeholders.  Final values MUST come
# from benchmark results or explicit configuration.
# ---------------------------------------------------------------------------

FAST_MODEL_PROFILE = ModelProfile(
    profile_id="fast_model_profile",
    model_id="",  # Provisional: set from benchmark results
    role="fast_triage",
    context_limit=0,  # Provisional: set from model capabilities
    default_completion_budget=0,
    max_completion_budget=0,
    timeout_seconds=0,
    supports_structured_output=False,
    supports_bilingual_responses=False,
    allowed_task_types=(
        TaskType.CODE_REVIEW,
        TaskType.CODEBASE_QUESTION,
        TaskType.UNKNOWN,
    ),
    escalation_target="deep_reasoning_model_profile",
    enabled=True,
)

DEEP_REASONING_MODEL_PROFILE = ModelProfile(
    profile_id="deep_reasoning_model_profile",
    model_id="",  # Provisional: set from benchmark results
    role="deep_reasoning",
    context_limit=0,  # Provisional: set from model capabilities
    default_completion_budget=0,
    max_completion_budget=0,
    timeout_seconds=0,
    supports_structured_output=False,
    supports_bilingual_responses=False,
    allowed_task_types=tuple(TaskType),
    escalation_target="",
    enabled=True,
)

FALLBACK_MODEL_PROFILE = ModelProfile(
    profile_id="fallback_model_profile",
    model_id="",  # Provisional: set from benchmark results
    role="fallback",
    context_limit=0,
    default_completion_budget=0,
    max_completion_budget=0,
    timeout_seconds=0,
    supports_structured_output=False,
    supports_bilingual_responses=False,
    allowed_task_types=tuple(TaskType),
    escalation_target="",
    enabled=True,
)


def get_profile_by_id(profile_id: str) -> ModelProfile | None:
    """Retrieve a profile template by its ID."""
    profiles = {
        FAST_MODEL_PROFILE.profile_id: FAST_MODEL_PROFILE,
        DEEP_REASONING_MODEL_PROFILE.profile_id: DEEP_REASONING_MODEL_PROFILE,
        FALLBACK_MODEL_PROFILE.profile_id: FALLBACK_MODEL_PROFILE,
    }
    return profiles.get(profile_id)


def build_cache_key(
    *,
    model_id: str = "",
    model_profile_version: str = "",
    prompt_schema_version: str = "",
    output_language: str = "",
    repository_fingerprint: str = "",
) -> CacheKey:
    """Construct a cache key for model output deduplication."""
    return CacheKey(
        model_id=model_id,
        model_profile_version=model_profile_version,
        prompt_schema_version=prompt_schema_version,
        output_language=output_language,
        repository_fingerprint=repository_fingerprint,
    )
