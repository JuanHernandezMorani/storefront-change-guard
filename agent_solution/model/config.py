"""Single-model runtime configuration.

The product runs exactly one local GGUF model per process through llama.cpp.
The selected Phase 03 runtime candidate is Qwen3.5-9B-UD-IQ3_XXS after the
controlled structured-output Gate A comparison recorded in
``docs/model-selection.md``.

The model path may be overridden for controlled verification. The runtime never
routes between models, retries with a fallback, or selects a model dynamically.
The artifact identity is derived from the actual GGUF filename so reports cannot
silently claim that a different model was used.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from agent_solution.analysis.models import SingleModelRuntimeConfig
from agent_solution.core.paths import project_root

# Selected single-model product profile.
_DEFAULT_MODEL_FILENAME = "Qwen3.5-9B-UD-IQ3_XXS.gguf"
_DEFAULT_RUNTIME_BACKEND = "llama.cpp"
_DEFAULT_RUNTIME_EXECUTABLE_NAME = "llama-cli"
_DEFAULT_CONTEXT_LIMIT = 8192
_DEFAULT_COMPLETION_LIMIT = 2048
_DEFAULT_TIMEOUT_SECONDS = 180
_DEFAULT_THREAD_COUNT = 12
_DEFAULT_THREAD_BATCH_COUNT = 12
_DEFAULT_BATCH_SIZE = 1024
_DEFAULT_MICRO_BATCH_SIZE = 512
_DEFAULT_TEMPERATURE = 0.0
_DEFAULT_TOP_P = 1.0
_DEFAULT_MIN_P = 0.1
_DEFAULT_REPEAT_PENALTY = 1.0
_DEFAULT_FLASH_ATTENTION = True
_DEFAULT_KV_CACHE_TYPE_K = "q8_0"
_DEFAULT_KV_CACHE_TYPE_V = "q8_0"
_DEFAULT_GPU_LAYERS = "auto"
_DEFAULT_PRIORITY = 3
_DEFAULT_PROMPT_SCHEMA_VERSION = "0.3.1"
_DEFAULT_RUNTIME_PROFILE_VERSION = "0.3.3"


def _resolve_runtime_executable_path() -> str:
    """Return the explicitly configured local llama-cli path or an empty string."""
    return os.environ.get("STORE_FRONT_GUARD_LLAMA_EXECUTABLE", "")


def _resolve_model_path() -> str:
    """Resolve the one selected model path for this process.

    Priority:
    1. ``STORE_FRONT_GUARD_MODEL_PATH`` for an explicit local deployment or a
       controlled verification run.
    2. The selected repository-relative product model path.

    An override replaces the single model for that process; it does not create
    fallback behavior or multi-model routing.
    """
    env_path = os.environ.get("STORE_FRONT_GUARD_MODEL_PATH", "")
    if env_path:
        return env_path
    return str(project_root() / "agent_solution" / "model" / _DEFAULT_MODEL_FILENAME)


def _model_identity_from_path(model_path: str) -> tuple[str, str]:
    """Return a stable, non-secret identity derived from the actual GGUF path.

    Only the filename is persisted in runtime artifacts. Absolute local paths
    remain private and are not used as model identifiers.
    """
    filename = Path(model_path.replace("\\", "/")).name or _DEFAULT_MODEL_FILENAME
    stem = Path(filename).stem.lower()
    model_id = re.sub(r"[^a-z0-9.]+", "-", stem).strip("-")
    return model_id, filename


def get_runtime_config() -> SingleModelRuntimeConfig:
    """Build the one-model runtime configuration from explicit local settings."""
    model_path = _resolve_model_path()
    model_id, model_filename = _model_identity_from_path(model_path)

    return SingleModelRuntimeConfig(
        model_id=model_id,
        model_filename=model_filename,
        model_path=model_path,
        runtime_backend=_DEFAULT_RUNTIME_BACKEND,
        runtime_executable_path=_resolve_runtime_executable_path(),
        runtime_executable_name=_DEFAULT_RUNTIME_EXECUTABLE_NAME,
        context_limit=_DEFAULT_CONTEXT_LIMIT,
        completion_limit=int(
            os.environ.get(
                "STORE_FRONT_GUARD_MODEL_COMPLETION_LIMIT",
                _DEFAULT_COMPLETION_LIMIT,
            )
        ),
        timeout_seconds=int(
            os.environ.get("STORE_FRONT_GUARD_MODEL_TIMEOUT", _DEFAULT_TIMEOUT_SECONDS)
        ),
        thread_count=int(
            os.environ.get("STORE_FRONT_GUARD_MODEL_THREADS", _DEFAULT_THREAD_COUNT)
        ),
        thread_batch_count=_DEFAULT_THREAD_BATCH_COUNT,
        batch_size=_DEFAULT_BATCH_SIZE,
        micro_batch_size=_DEFAULT_MICRO_BATCH_SIZE,
        temperature=_DEFAULT_TEMPERATURE,
        top_p=_DEFAULT_TOP_P,
        min_p=_DEFAULT_MIN_P,
        repeat_penalty=_DEFAULT_REPEAT_PENALTY,
        flash_attention_enabled=_DEFAULT_FLASH_ATTENTION,
        kv_cache_type_k=_DEFAULT_KV_CACHE_TYPE_K,
        kv_cache_type_v=_DEFAULT_KV_CACHE_TYPE_V,
        gpu_layers=_DEFAULT_GPU_LAYERS,
        priority=_DEFAULT_PRIORITY,
        prompt_schema_version=_DEFAULT_PROMPT_SCHEMA_VERSION,
        runtime_profile_version=_DEFAULT_RUNTIME_PROFILE_VERSION,
    )
