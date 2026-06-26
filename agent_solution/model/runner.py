"""Local model runner using llama-cli (Test 1 profile).

Executes a single model invocation via subprocess with strict safety:
- shell=False
- argument arrays
- explicit timeouts
- bounded stdout/stderr capture
- no retries
- no fallback models
- non-interactive completion only

Profile reconciled with Test 1 successful runtime evidence.
Uses llama-cli with prompt-file transport (-f), UTF-8 prompt content,
final newline, stdin=DEVNULL, --no-display-prompt, -st, and --jinja.
"""

from __future__ import annotations

import subprocess
import tempfile
import time
from pathlib import Path

from agent_solution.analysis.models import (
    ModelExecutionResult,
    SingleModelRuntimeConfig,
)


def _build_command(
    config: SingleModelRuntimeConfig,
    prompt_file_path: str,
) -> tuple[str, ...]:
    """Build the llama-cli command tuple (Test 1 profile).

    Returns the full command as a tuple for subprocess execution.
    Uses -f for prompt file to avoid interactive mode and shell quoting issues.
    Uses -st for single-turn non-interactive completion.
    Uses --jinja for chat-template rendering (llama-cli default, but explicit).
    Uses --no-display-prompt to suppress prompt echo.
    Uses -ngl auto for GPU offloading.
    Uses --flash-attn on for flash attention.
    Uses -ctk/-ctv q8_0 for KV cache types.

    Note: llama-cli does NOT support --reasoning-budget or -no-cnv at runtime.
    The Qwen model's reasoning mode is handled by the output envelope parser.
    """
    cmd = [
        config.runtime_executable_path,
        "-m", config.model_path,
        "-ngl", config.gpu_layers,
        "-c", str(config.context_limit),
        "-n", str(config.completion_limit),
        "-t", str(config.thread_count),
        "-tb", str(config.thread_batch_count),
        "-b", str(config.batch_size),
        "-ub", str(config.micro_batch_size),
        "--temp", str(config.temperature),
        "--top-p", str(config.top_p),
        "--min-p", str(config.min_p),
        "--repeat-penalty", str(config.repeat_penalty),
        "--prio", str(config.priority),
    ]

    if config.flash_attention_enabled:
        cmd.extend(["--flash-attn", "on"])

    if config.kv_cache_type_k:
        cmd.extend(["-ctk", config.kv_cache_type_k])
    if config.kv_cache_type_v:
        cmd.extend(["-ctv", config.kv_cache_type_v])

    # Test 1 profile: llama-cli with --jinja, -st, -f, --no-display-prompt
    # Note: --reasoning-budget and -no-cnv are NOT supported by llama-cli
    cmd.extend([
        "--jinja",
        "--no-display-prompt",
        "-st",
        "-f", prompt_file_path,
    ])

    return tuple(cmd)


def run_model(
    config: SingleModelRuntimeConfig,
    prompt: str,
    max_output_bytes: int = 131072,
) -> ModelExecutionResult:
    """Execute a single model invocation.

    Returns ModelExecutionResult with stdout, stderr, exit code, and timing.
    Never retries.  Never falls back to another model.
    Uses temporary prompt file for safe transport.
    """
    if not config.runtime_executable_path:
        return ModelExecutionResult(
            success=False,
            stdout="",
            stderr="Runtime executable not configured",
            exit_code=-1,
            timed_out=False,
            duration_ms=0,
            error_message="MODEL_UNAVAILABLE: runtime executable path not configured",
        )

    if not Path(config.runtime_executable_path).exists():
        return ModelExecutionResult(
            success=False,
            stdout="",
            stderr=f"Runtime executable not found at: {config.runtime_executable_path}",
            exit_code=-1,
            timed_out=False,
            duration_ms=0,
            error_message=f"MODEL_UNAVAILABLE: {config.runtime_executable_path} not found",
        )

    if not Path(config.model_path).exists():
        return ModelExecutionResult(
            success=False,
            stdout="",
            stderr=f"Model file not found at: {config.model_path}",
            exit_code=-1,
            timed_out=False,
            duration_ms=0,
            error_message=f"MODEL_UNAVAILABLE: model file not found at {config.model_path}",
        )

    # Create temporary prompt file for safe transport
    tmp_file = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            encoding="utf-8",
            delete=False,
        )
        # Write prompt with final newline (Test 1 pattern)
        tmp_file.write(prompt)
        if not prompt.endswith("\n"):
            tmp_file.write("\n")
        tmp_file.flush()
        tmp_file.close()
        
        prompt_file_path = tmp_file.name
        cmd = _build_command(config, prompt_file_path)

        start = time.monotonic()
        timed_out = False
        process = None
        try:
            process = subprocess.Popen(
                [str(c) for c in cmd],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            
            try:
                stdout, stderr = process.communicate(timeout=config.timeout_seconds)
                exit_code = process.returncode
                stdout = stdout[:max_output_bytes]
                stderr = stderr[:max_output_bytes]
            except subprocess.TimeoutExpired:
                timed_out = True
                exit_code = -1
                stdout = ""
                stderr = f"Model execution timed out after {config.timeout_seconds}s"
                
                # Cleanup the child process safely
                try:
                    process.kill()
                    process.wait(timeout=5)
                except Exception:  # noqa: BLE001
                    pass
        except FileNotFoundError:
            return ModelExecutionResult(
                success=False,
                stdout="",
                stderr=f"Executable not found: {config.runtime_executable_path}",
                exit_code=-1,
                timed_out=False,
                duration_ms=0,
                error_message="MODEL_UNAVAILABLE: executable not found",
            )
        except Exception as exc:  # noqa: BLE001
            return ModelExecutionResult(
                success=False,
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                timed_out=False,
                duration_ms=0,
                error_message=f"MODEL_EXECUTION_FAILED: {exc}",
            )

        duration_ms = int((time.monotonic() - start) * 1000)
        success = exit_code == 0 and not timed_out

        return ModelExecutionResult(
            success=success,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=timed_out,
            duration_ms=duration_ms,
            command=cmd,
            error_message="" if success else f"exit_code={exit_code}",
        )
    finally:
        # Clean up temporary prompt file
        if tmp_file and tmp_file.name:
            try:
                Path(tmp_file.name).unlink(missing_ok=True)
            except Exception:  # noqa: BLE001
                pass
