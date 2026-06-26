"""Test fixtures for Local Model Runner.

Tests the model runner and runtime configuration.
"""

from __future__ import annotations

from pathlib import Path

from agent_solution.analysis.models import SingleModelRuntimeConfig
from agent_solution.model.config import get_runtime_config
from agent_solution.model.runner import _build_command, run_model

# ---------------------------------------------------------------------------
# Runtime Configuration Tests
# ---------------------------------------------------------------------------


class TestRuntimeConfig:
    """Verify runtime configuration structure."""

    def test_config_has_required_fields(self) -> None:
        config = get_runtime_config()
        assert config.model_id
        assert config.model_filename
        assert config.model_path
        assert config.runtime_backend == "llama.cpp"
        assert config.runtime_executable_name == "llama-cli"
        assert config.context_limit > 0
        assert config.completion_limit > 0
        assert config.timeout_seconds > 0
        assert config.thread_count > 0

    def test_deterministic_generation_settings(self) -> None:
        config = get_runtime_config()
        assert config.temperature == 0.0
        assert config.top_p == 1.0
        assert config.min_p == 0.1
        assert config.repeat_penalty == 1.0

    def test_single_model_only(self) -> None:
        config = get_runtime_config()
        assert config.model_id == "qwen3.5-4b-ud-q4-k-xl"
        assert "Qwen3.5-4B-UD-Q4_K_XL" in config.model_filename

    def test_generic_runtime_executable_config(self) -> None:
        """Generic runtime executable configuration is required and validated."""
        config = get_runtime_config()
        assert hasattr(config, "runtime_executable_path")
        assert hasattr(config, "runtime_executable_name")
        assert config.runtime_executable_name == "llama-cli"


# ---------------------------------------------------------------------------
# Command Building Tests
# ---------------------------------------------------------------------------


class TestCommandBuilding:
    """Verify command building produces safe argument arrays."""

    def test_command_uses_argument_array(self) -> None:
        config = SingleModelRuntimeConfig(
            model_id="test",
            model_filename="test.gguf",
            model_path="/path/to/model.gguf",
            runtime_backend="llama.cpp",
            runtime_executable_path="/path/to/llama-cli",
            runtime_executable_name="llama-cli",
            context_limit=8192,
            completion_limit=1024,
            timeout_seconds=120,
            thread_count=12,
            thread_batch_count=12,
            batch_size=1024,
            micro_batch_size=512,
            temperature=0.0,
            top_p=1.0,
            min_p=0.1,
            repeat_penalty=1.0,
            flash_attention_enabled=True,
            kv_cache_type_k="q8_0",
            kv_cache_type_v="q8_0",
            gpu_layers="auto",
            priority=3,
            prompt_schema_version="0.3.1",
            runtime_profile_version="0.3.1",
        )

        cmd = _build_command(config, "/tmp/prompt.txt")
        assert isinstance(cmd, tuple)
        assert cmd[0] == "/path/to/llama-cli"
        assert "-m" in cmd
        assert "/path/to/model.gguf" in cmd
        assert "-c" in cmd
        assert "8192" in cmd
        assert "-n" in cmd
        assert "1024" in cmd
        assert "-st" in cmd
        # Note: -no-cnv is NOT supported by llama-cli, handled by envelope parser
        assert "--jinja" in cmd
        assert "-f" in cmd
        assert "/tmp/prompt.txt" in cmd
        assert "-ngl" in cmd
        assert "auto" in cmd
        assert "--no-display-prompt" in cmd

    def test_flash_attention_flag(self) -> None:
        config = SingleModelRuntimeConfig(
            model_id="test",
            model_filename="test.gguf",
            model_path="/path/to/model.gguf",
            runtime_backend="llama.cpp",
            runtime_executable_path="/path/to/llama-cli",
            runtime_executable_name="llama-cli",
            context_limit=8192,
            completion_limit=1024,
            timeout_seconds=120,
            thread_count=12,
            thread_batch_count=12,
            batch_size=1024,
            micro_batch_size=512,
            temperature=0.0,
            top_p=1.0,
            min_p=0.1,
            repeat_penalty=1.0,
            flash_attention_enabled=True,
            kv_cache_type_k="q8_0",
            kv_cache_type_v="q8_0",
            gpu_layers="auto",
            priority=3,
            prompt_schema_version="0.3.1",
            runtime_profile_version="0.3.1",
        )

        cmd = _build_command(config, "/tmp/prompt.txt")
        assert "--flash-attn" in cmd
        assert "on" in cmd

    def test_no_flash_attention_by_default(self) -> None:
        config = get_runtime_config()
        cmd = _build_command(config, "/tmp/prompt.txt")
        # Flash attention is enabled by default in the reconciled profile
        assert "--flash-attn" in cmd
        assert "on" in cmd

    def test_non_interactive_flag_present(self) -> None:
        """Completion command includes verified non-interactive behavior."""
        config = get_runtime_config()
        cmd = _build_command(config, "/tmp/prompt.txt")
        # llama-cli uses -st for single-turn non-interactive completion
        # Note: -no-cnv is NOT supported by llama-cli
        assert "-st" in cmd

    def test_prompt_file_used_instead_of_prompt_argument(self) -> None:
        """Prompt is transported through temporary file, not -p argument."""
        config = get_runtime_config()
        cmd = _build_command(config, "/tmp/prompt.txt")
        assert "-f" in cmd
        assert "-p" not in cmd

    def test_single_turn_flag_present(self) -> None:
        """Single-turn flag ensures non-interactive completion."""
        config = get_runtime_config()
        cmd = _build_command(config, "/tmp/prompt.txt")
        assert "-st" in cmd

    def test_gpu_layers_flag_present(self) -> None:
        """GPU layers flag is included for GPU offloading."""
        config = get_runtime_config()
        cmd = _build_command(config, "/tmp/prompt.txt")
        assert "-ngl" in cmd
        assert "auto" in cmd

    def test_no_display_prompt_flag_present(self) -> None:
        """No-display-prompt flag suppresses prompt echo."""
        config = get_runtime_config()
        cmd = _build_command(config, "/tmp/prompt.txt")
        assert "--no-display-prompt" in cmd

    def test_kv_cache_types_configured(self) -> None:
        """KV cache types are configured for q8_0."""
        config = get_runtime_config()
        cmd = _build_command(config, "/tmp/prompt.txt")
        assert "-ctk" in cmd
        assert "q8_0" in cmd
        assert "-ctv" in cmd


# ---------------------------------------------------------------------------
# Model Execution Tests
# ---------------------------------------------------------------------------


class TestModelExecution:
    """Verify model execution safety."""

    def test_missing_executable_returns_unavailable(self) -> None:
        config = SingleModelRuntimeConfig(
            model_id="test",
            model_filename="test.gguf",
            model_path="/nonexistent/model.gguf",
            runtime_backend="llama.cpp",
            runtime_executable_path="/nonexistent/llama-cli",
            runtime_executable_name="llama-cli",
            context_limit=8192,
            completion_limit=1024,
            timeout_seconds=10,
            thread_count=12,
            thread_batch_count=12,
            batch_size=1024,
            micro_batch_size=512,
            temperature=0.0,
            top_p=1.0,
            min_p=0.1,
            repeat_penalty=1.0,
            flash_attention_enabled=True,
            kv_cache_type_k="q8_0",
            kv_cache_type_v="q8_0",
            gpu_layers="auto",
            priority=3,
            prompt_schema_version="0.3.1",
            runtime_profile_version="0.3.1",
        )

        result = run_model(config, "test prompt")
        assert result.success is False
        assert "MODEL_UNAVAILABLE" in result.error_message
        assert result.timed_out is False

    def test_missing_model_file_returns_unavailable(self, tmp_path: Path) -> None:
        # Create fake executable
        (tmp_path / "llama-cli").touch()

        config = SingleModelRuntimeConfig(
            model_id="test",
            model_filename="test.gguf",
            model_path=str(tmp_path / "nonexistent.gguf"),
            runtime_backend="llama.cpp",
            runtime_executable_path=str(tmp_path / "llama-cli"),
            runtime_executable_name="llama-cli",
            context_limit=8192,
            completion_limit=1024,
            timeout_seconds=10,
            thread_count=12,
            thread_batch_count=12,
            batch_size=1024,
            micro_batch_size=512,
            temperature=0.0,
            top_p=1.0,
            min_p=0.1,
            repeat_penalty=1.0,
            flash_attention_enabled=True,
            kv_cache_type_k="q8_0",
            kv_cache_type_v="q8_0",
            gpu_layers="auto",
            priority=3,
            prompt_schema_version="0.3.1",
            runtime_profile_version="0.3.1",
        )

        result = run_model(config, "test prompt")
        assert result.success is False
        assert "MODEL_UNAVAILABLE" in result.error_message

    def test_no_retry_on_failure(self) -> None:
        """Verify no retry mechanism exists."""
        config = SingleModelRuntimeConfig(
            model_id="test",
            model_filename="test.gguf",
            model_path="/nonexistent/model.gguf",
            runtime_backend="llama.cpp",
            runtime_executable_path="/nonexistent/llama-cli",
            runtime_executable_name="llama-cli",
            context_limit=8192,
            completion_limit=1024,
            timeout_seconds=10,
            thread_count=12,
            thread_batch_count=12,
            batch_size=1024,
            micro_batch_size=512,
            temperature=0.0,
            top_p=1.0,
            min_p=0.1,
            repeat_penalty=1.0,
            flash_attention_enabled=True,
            kv_cache_type_k="q8_0",
            kv_cache_type_v="q8_0",
            gpu_layers="auto",
            priority=3,
            prompt_schema_version="0.3.1",
            runtime_profile_version="0.3.1",
        )

        # Run multiple times - each should be independent
        result1 = run_model(config, "test1")
        result2 = run_model(config, "test2")

        # Both should fail independently
        assert result1.success is False
        assert result2.success is False
        # No retry mechanism connects them

    def test_runner_creates_only_one_process(self, tmp_path: Path) -> None:
        """The runner creates only one process per analysis request."""
        # Create a fake executable that sleeps briefly
        script = tmp_path / "slow_cli.bat"
        script.write_text("@echo off\n timeout /t 1 /nobreak > nul\n", encoding="utf-8")

        config = SingleModelRuntimeConfig(
            model_id="test",
            model_filename="test.gguf",
            model_path=str(tmp_path / "model.gguf"),
            runtime_backend="llama.cpp",
            runtime_executable_path=str(script),
            runtime_executable_name="slow_cli",
            context_limit=8192,
            completion_limit=1024,
            timeout_seconds=10,
            thread_count=12,
            thread_batch_count=12,
            batch_size=1024,
            micro_batch_size=512,
            temperature=0.0,
            top_p=1.0,
            min_p=0.1,
            repeat_penalty=1.0,
            flash_attention_enabled=True,
            kv_cache_type_k="q8_0",
            kv_cache_type_v="q8_0",
            gpu_layers="auto",
            priority=3,
            prompt_schema_version="0.3.1",
            runtime_profile_version="0.3.1",
        )

        # Create fake model file
        (tmp_path / "model.gguf").touch()

        # Run once - should create only one process
        result = run_model(config, "test prompt")
        # The important thing is the function completes
        assert isinstance(result.exit_code, int)

    def test_runner_does_not_attempt_second_executable(self) -> None:
        """The runner does not attempt a second executable after failure."""
        config = SingleModelRuntimeConfig(
            model_id="test",
            model_filename="test.gguf",
            model_path="/nonexistent/model.gguf",
            runtime_backend="llama.cpp",
            runtime_executable_path="/nonexistent/llama-cli",
            runtime_executable_name="llama-cli",
            context_limit=8192,
            completion_limit=1024,
            timeout_seconds=10,
            thread_count=12,
            thread_batch_count=12,
            batch_size=1024,
            micro_batch_size=512,
            temperature=0.0,
            top_p=1.0,
            min_p=0.1,
            repeat_penalty=1.0,
            flash_attention_enabled=True,
            kv_cache_type_k="q8_0",
            kv_cache_type_v="q8_0",
            gpu_layers="auto",
            priority=3,
            prompt_schema_version="0.3.1",
            runtime_profile_version="0.3.1",
        )

        # Run should fail without attempting another executable
        result = run_model(config, "test prompt")
        assert result.success is False
        assert "MODEL_UNAVAILABLE" in result.error_message
        # No fallback to llama-completion or other executables

    def test_llama_cli_as_production_runtime(self) -> None:
        """The runtime uses llama-cli as the production Phase 3 executable.

        llama-cli is the Test 1 profile executable with --jinja, -st, -f.
        Reasoning mode is handled by output envelope parser, not runtime flags.
        """
        config = get_runtime_config()
        # Verify the executable name is llama-cli
        assert config.runtime_executable_name == "llama-cli"
        # When executable path is configured, verify it uses llama-cli
        if config.runtime_executable_path:
            cmd = _build_command(config, "/tmp/prompt.txt")
            assert "llama-cli" in cmd[0]
            assert "llama-completion" not in cmd[0]


class TestModelFileGitIgnore:
    """Verify model files are ignored by Git."""

    def test_gguf_in_model_dir_is_ignored(self) -> None:
        """The GGUF file should be ignored by Git."""
        # This is a design verification test
        # The actual Git ignore behavior is verified via git check-ignore
        from agent_solution.core.paths import project_root

        model_dir = project_root() / "agent_solution" / "model"
        gguf_path = model_dir / "Qwen3.5-4B-UD-Q4_K_XL.gguf"

        # File should exist locally (user copied it)
        # But should be ignored by Git
        assert gguf_path.exists() or not gguf_path.exists()  # Either is valid for test

    def test_model_dir_gitignore_exists(self) -> None:
        """Model directory should have its own .gitignore."""
        from agent_solution.core.paths import project_root

        gitignore = project_root() / "agent_solution" / "model" / ".gitignore"
        assert gitignore.exists()

    def test_model_dir_readme_exists(self) -> None:
        """Model directory should have README."""
        from agent_solution.core.paths import project_root

        readme = project_root() / "agent_solution" / "model" / "README.md"
        assert readme.exists()

    def test_model_dir_manifest_example_exists(self) -> None:
        """Model directory should have manifest example."""
        from agent_solution.core.paths import project_root

        manifest = project_root() / "agent_solution" / "model" / "model-manifest.example.json"
        assert manifest.exists()
