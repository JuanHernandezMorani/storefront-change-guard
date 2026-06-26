"""Single-model runtime configuration.

Provides the operational configuration for the Qwen3.5-4B model
using llama.cpp CLI.  Profile reconciled with Test 1 successful
runtime evidence.
"""

from __future__ import annotations

import os

from agent_solution.analysis.models import SingleModelRuntimeConfig
from agent_solution.core.paths import project_root

# Default model configuration
_DEFAULT_MODEL_FILENAME = "Qwen3.5-4B-UD-Q4_K_XL.gguf"
_DEFAULT_MODEL_ID = "qwen3.5-4b-ud-q4-k-xl"
_DEFAULT_RUNTIME_BACKEND = "llama.cpp"
_DEFAULT_RUNTIME_EXECUTABLE_NAME = "llama-cli"
_DEFAULT_CONTEXT_LIMIT = 8192
_DEFAULT_COMPLETION_LIMIT = 1024
_DEFAULT_TIMEOUT_SECONDS = 120
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
_DEFAULT_RUNTIME_PROFILE_VERSION = "0.3.1"


def _resolve_runtime_executable_path() -> str:
    """Resolve the runtime executable path.

    Priority:
    1. STORE_FRONT_GUARD_LLAMA_EXECUTABLE environment variable
    2. Empty string (will cause MODEL_UNAVAILABLE)

    No auto-discovery from hardcoded paths. User must provide explicit path.
    The selected executable is llama-cli, which has direct empirical local
    evidence of successful one-shot operation with the Qwen model (Test 1).
    """
    return os.environ.get("STORE_FRONT_GUARD_LLAMA_EXECUTABLE", "")


def _resolve_model_path() -> str:
    """Resolve the model file path.

    Priority:
    1. STORE_FRONT_GUARD_MODEL_PATH environment variable
    2. Default relative path from repository root
    """
    env_path = os.environ.get("STORE_FRONT_GUARD_MODEL_PATH", "")
    if env_path:
        return env_path

    return str(project_root() / "agent_solution" / "model" / _DEFAULT_MODEL_FILENAME)


def get_runtime_config() -> SingleModelRuntimeConfig:
    """Build the runtime configuration from environment and defaults.

    Uses the Test 1 reconciled profile:
    - llama-cli as the single selected executable
    - --jinja enabled (llama-cli default, explicit for clarity)
    - -st for single-turn non-interactive completion
    - Prompt file transport (-f)
    - Conservative context limit (8192) with completion budget (1024)
    - Reasoning mode handled by output envelope parser (not runtime flags)
    """
    return SingleModelRuntimeConfig(
        model_id=_DEFAULT_MODEL_ID,
        model_filename=_DEFAULT_MODEL_FILENAME,
        model_path=_resolve_model_path(),
        runtime_backend=_DEFAULT_RUNTIME_BACKEND,
        runtime_executable_path=_resolve_runtime_executable_path(),
        runtime_executable_name=_DEFAULT_RUNTIME_EXECUTABLE_NAME,
        context_limit=_DEFAULT_CONTEXT_LIMIT,
        completion_limit=_DEFAULT_COMPLETION_LIMIT,
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
