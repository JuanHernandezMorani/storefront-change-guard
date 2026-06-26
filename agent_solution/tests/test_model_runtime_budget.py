from __future__ import annotations

from agent_solution.model.config import get_runtime_config


def test_default_runtime_budget_supports_reasoning_then_structured_json(
    monkeypatch,
) -> None:
    monkeypatch.delenv("STORE_FRONT_GUARD_MODEL_COMPLETION_LIMIT", raising=False)
    monkeypatch.delenv("STORE_FRONT_GUARD_MODEL_TIMEOUT", raising=False)

    config = get_runtime_config()

    assert config.context_limit == 8192
    assert config.completion_limit == 2048
    assert config.timeout_seconds == 180
    assert config.runtime_profile_version == "0.3.2"


def test_completion_budget_can_be_explicitly_overridden(monkeypatch) -> None:
    monkeypatch.setenv("STORE_FRONT_GUARD_MODEL_COMPLETION_LIMIT", "2304")

    config = get_runtime_config()

    assert config.completion_limit == 2304
