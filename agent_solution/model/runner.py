"""Local model runner using llama-cli (Test 1 profile).

Executes exactly one local model invocation via subprocess with strict safety:
- shell=False and argument arrays
- explicit timeout and bounded capture
- no retries and no fallback model
- non-interactive prompt-file transport
- deterministic sanitization of known llama-cli stdout wrappers before parsing

The model-facing output is never allowed to include llama-cli's banner, prompt
 echo, or performance trailer.  The raw process output stays transient inside
this module; callers receive only the sanitized model response plus compact
sanitization metadata.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
import time
from pathlib import Path

from agent_solution.analysis.models import (
    ModelExecutionResult,
    SingleModelRuntimeConfig,
)

# These patterns are intentionally narrow.  They remove only output that the
# observed llama-cli build prints outside the model response.  They are not a
# general JSON extractor and do not relax the strict envelope parser.
_TRAILER_PATTERN = re.compile(
    r"\n?\s*\[\s*Prompt:\s*[^\]\r\n]*\]\s*\n+\s*Exiting\.\.\.\s*\Z",
    re.DOTALL,
)
_START_THINKING = "[Start thinking]"
_END_THINKING = "[End thinking]"


def _build_command(
    config: SingleModelRuntimeConfig,
    prompt_file_path: str,
) -> tuple[str, ...]:
    """Build the llama-cli command tuple for the empirically selected profile."""
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

    # Test 1 profile: explicit chat template, one-shot completion, prompt file.
    cmd.extend([
        "--jinja",
        "--no-display-prompt",
        "-st",
        "-f", prompt_file_path,
    ])
    return tuple(cmd)


def _strip_known_cli_prefix(raw_stdout: str, prompt: str) -> tuple[str, tuple[str, ...]]:
    """Strip the observed llama-cli banner and exact prompt echo, if present.

    The banner is stripped only when the prompt echo matches the exact prompt
    sent by this runner.  That prevents arbitrary prose from being discarded
    merely because it appears before a JSON-looking payload.
    """
    prompt_without_final_newline = prompt.rstrip("\r\n")
    if not prompt_without_final_newline:
        return raw_stdout, ()

    # On Windows the temporary prompt file is written in text mode.  The
    # observed llama-cli echo can therefore use CRLF even when the Python
    # prompt string uses LF.  Accept only newline-equivalent copies of the
    # *exact* prompt; do not search for arbitrary JSON or prose.
    prompt_variants = (
        prompt_without_final_newline,
        prompt_without_final_newline.replace("\n", "\r\n"),
        prompt_without_final_newline.replace("\n", "\r"),
    )
    echo_index = -1
    echo_length = 0
    for prompt_variant in prompt_variants:
        echo = "> " + prompt_variant
        candidate_index = raw_stdout.find(echo)
        if candidate_index >= 0:
            echo_index = candidate_index
            echo_length = len(echo)
            break

    if echo_index < 0:
        return raw_stdout, ()

    prefix = raw_stdout[:echo_index]
    # A verified CLI wrapper always begins with the observed loading banner.
    # Without it, preserve the output for the strict envelope parser to reject.
    if not prefix.lstrip().startswith("Loading model..."):
        return raw_stdout, ()

    response_start = echo_index + echo_length
    return raw_stdout[response_start:], ("LLAMA_CLI_BANNER_AND_PROMPT_ECHO_STRIPPED",)


def _strip_known_cli_trailer(candidate: str) -> tuple[str, tuple[str, ...]]:
    """Remove only llama-cli's terminal performance/exiting trailer."""
    match = _TRAILER_PATTERN.search(candidate)
    if match is None:
        return candidate, ()
    return candidate[:match.start()], ("LLAMA_CLI_PERFORMANCE_TRAILER_STRIPPED",)


def _normalize_observed_thinking_tags(candidate: str) -> tuple[str, tuple[str, ...]]:
    """Convert one leading observed llama-cli thinking pair to the strict form.

    This accepts only one complete leading `[Start thinking]...[End thinking]`
    pair.  Incomplete, repeated, or embedded pairs are left untouched so the
    strict envelope parser can reject them deterministically.
    """
    leading = candidate.lstrip()
    if not leading.startswith(_START_THINKING):
        return candidate, ()

    content_start = len(_START_THINKING)
    end_index = leading.find(_END_THINKING, content_start)
    if end_index < 0:
        return candidate, ()

    after_end = leading[end_index + len(_END_THINKING):]
    reasoning_content = leading[content_start:end_index]
    if _START_THINKING in reasoning_content or _END_THINKING in after_end:
        return candidate, ()

    normalized = f"<think>{reasoning_content}</think>{after_end}"
    return normalized, ("OBSERVED_THINKING_TAGS_NORMALIZED",)


def sanitize_llama_cli_stdout(raw_stdout: str, prompt: str) -> tuple[str, tuple[str, ...]]:
    """Return strict-parser input plus compact sanitization categories.

    This function is deliberately *not* a permissive parser.  It only removes
    the known deterministic wrapper emitted by the local llama-cli build and
    normalizes the one observed leading thinking-pair spelling.  Any other
    prose remains and will be rejected by `extract_reasoning_envelope`.
    """
    candidate, categories = _strip_known_cli_prefix(raw_stdout, prompt)
    candidate, trailer_categories = _strip_known_cli_trailer(candidate)
    candidate, thinking_categories = _normalize_observed_thinking_tags(candidate)
    return candidate.strip(), categories + trailer_categories + thinking_categories


def _result(
    *,
    success: bool,
    stdout: str,
    stderr: str,
    exit_code: int,
    timed_out: bool,
    duration_ms: int,
    command: tuple[str, ...] = (),
    error_message: str = "",
    raw_stdout_byte_count: int = 0,
    sanitization_categories: tuple[str, ...] = (),
) -> ModelExecutionResult:
    """Create a result without exposing transient raw stdout."""
    return ModelExecutionResult(
        success=success,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        timed_out=timed_out,
        duration_ms=duration_ms,
        command=command,
        error_message=error_message,
        raw_stdout_byte_count=raw_stdout_byte_count,
        stdout_sanitization_categories=sanitization_categories,
    )


def run_model(
    config: SingleModelRuntimeConfig,
    prompt: str,
    max_output_bytes: int = 131072,
) -> ModelExecutionResult:
    """Execute exactly one local model invocation.

    Raw stdout is kept only long enough to sanitize the deterministic CLI
    wrapper.  It is never returned or persisted by this function.
    """
    if not config.runtime_executable_path:
        return _result(
            success=False,
            stdout="",
            stderr="Runtime executable not configured",
            exit_code=-1,
            timed_out=False,
            duration_ms=0,
            error_message="MODEL_UNAVAILABLE: runtime executable path not configured",
        )

    if not Path(config.runtime_executable_path).exists():
        return _result(
            success=False,
            stdout="",
            stderr=f"Runtime executable not found at: {config.runtime_executable_path}",
            exit_code=-1,
            timed_out=False,
            duration_ms=0,
            error_message=f"MODEL_UNAVAILABLE: {config.runtime_executable_path} not found",
        )

    if not Path(config.model_path).exists():
        return _result(
            success=False,
            stdout="",
            stderr=f"Model file not found at: {config.model_path}",
            exit_code=-1,
            timed_out=False,
            duration_ms=0,
            error_message=f"MODEL_UNAVAILABLE: model file not found at {config.model_path}",
        )

    tmp_file = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            encoding="utf-8",
            delete=False,
        )
        tmp_file.write(prompt)
        if not prompt.endswith("\n"):
            tmp_file.write("\n")
        tmp_file.flush()
        tmp_file.close()

        cmd = _build_command(config, tmp_file.name)
        start = time.monotonic()
        try:
            process = subprocess.Popen(
                [str(component) for component in cmd],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            try:
                raw_stdout, stderr = process.communicate(timeout=config.timeout_seconds)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                    process.wait(timeout=5)
                except Exception:  # noqa: BLE001
                    pass
                return _result(
                    success=False,
                    stdout="",
                    stderr=f"Model execution timed out after {config.timeout_seconds}s",
                    exit_code=-1,
                    timed_out=True,
                    duration_ms=int((time.monotonic() - start) * 1000),
                    command=cmd,
                    error_message=f"MODEL_TIMEOUT: exceeded {config.timeout_seconds}s",
                )
        except FileNotFoundError:
            return _result(
                success=False,
                stdout="",
                stderr=f"Executable not found: {config.runtime_executable_path}",
                exit_code=-1,
                timed_out=False,
                duration_ms=0,
                command=cmd,
                error_message="MODEL_UNAVAILABLE: executable not found",
            )
        except Exception as exc:  # noqa: BLE001
            return _result(
                success=False,
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                timed_out=False,
                duration_ms=0,
                command=cmd,
                error_message=f"MODEL_EXECUTION_FAILED: {exc}",
            )

        raw_stdout = raw_stdout[:max_output_bytes]
        stderr = stderr[:max_output_bytes]
        sanitized_stdout, categories = sanitize_llama_cli_stdout(raw_stdout, prompt)
        duration_ms = int((time.monotonic() - start) * 1000)
        success = exit_code == 0
        return _result(
            success=success,
            stdout=sanitized_stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=False,
            duration_ms=duration_ms,
            command=cmd,
            error_message="" if success else f"exit_code={exit_code}",
            raw_stdout_byte_count=len(raw_stdout.encode("utf-8")),
            sanitization_categories=categories,
        )
    finally:
        if tmp_file and tmp_file.name:
            try:
                Path(tmp_file.name).unlink(missing_ok=True)
            except Exception:  # noqa: BLE001
                pass
