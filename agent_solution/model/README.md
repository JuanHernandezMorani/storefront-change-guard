# Model Directory

This directory contains model files for Phase 03 evidence-grounded analysis.

## Contents

- `Qwen3.5-4B-UD-Q4_K_XL.gguf` - Local model file (not tracked in Git)
- `README.md` - This file
- `model-manifest.example.json` - Example manifest structure
- `.gitignore` - Git ignore rules for model binaries

## Model File

The model file is expected at:

```text
agent_solution/model/Qwen3.5-4B-UD-Q4_K_XL.gguf
```

This file is ignored by Git and must be obtained separately.

## Configuration

Model runtime is configured via environment variables:

```text
STORE_FRONT_GUARD_LLAMA_EXECUTABLE - Path to llama-completion executable (required)
STORE_FRONT_GUARD_MODEL_PATH - Path to model file
STORE_FRONT_GUARD_MODEL_TIMEOUT - Timeout in seconds
STORE_FRONT_GUARD_MODEL_THREADS - Number of threads
```

The runtime uses `llama-completion` with `-no-cnv` flag for non-interactive completion.
No auto-discovery or fallback executables are used. The user must provide the explicit path.

## Git Ignore

Model binaries are ignored via `.gitignore`:

```text
*.gguf
*.bin
*.safetensors
*.pt
*.pth
*.onnx
```

Only lightweight metadata files are tracked.
