<#
.SYNOPSIS
Runs the controlled Phase 04 live validation without modifying the source checkout.

.DESCRIPTION
Creates an ignored artifact directory, generates a deterministic candidate patch from
<BaseRef>:shipping.py, validates it only in a detached Git worktree through the
Storefront Change Guard Phase 04 CLI, and proves that the source checkout's Git
status is unchanged before and after the run.

The candidate addresses the low-severity "hardcoded shipping rate" review finding
by replacing the magic 700-cent value with STANDARD_SHIPPING_CENTS and adding two
shipping behavior tests. The candidate patch is never applied to the source checkout.
#>

[CmdletBinding()]
param(
    [string]$Repository = (Split-Path -Parent $PSScriptRoot),
    [string]$BaseRef = "HEAD",
    [string]$ArtifactRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Get-GitStatusSnapshot {
    param([Parameter(Mandatory)][string]$RepositoryPath)

    $lines = & git -C $RepositoryPath status --porcelain=v1 --untracked-files=all
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed for the source checkout."
    }
    return ($lines -join "`n")
}

$repositoryItem = Get-Item -LiteralPath $Repository -ErrorAction Stop
if (-not $repositoryItem.PSIsContainer) {
    throw "Repository must be a directory: $Repository"
}
$repositoryPath = $repositoryItem.FullName

$python = Join-Path $repositoryPath ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $python = "python"
}

$resolvedBaseRef = (& git -C $repositoryPath rev-parse "$BaseRef^{commit}").Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($resolvedBaseRef)) {
    throw "Base ref does not resolve to a commit: $BaseRef"
}

$root = if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) {
    Join-Path $repositoryPath "artifacts\phase04-live"
} else {
    $ArtifactRoot
}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDirectory = Join-Path $root "run-$timestamp"
New-Item -ItemType Directory -Path $runDirectory -Force | Out-Null

$beforeStatus = Get-GitStatusSnapshot -RepositoryPath $repositoryPath
$patchPath = Join-Path $runDirectory "candidate-shipping-rate-constant.patch"
$generatorOutputPath = Join-Path $runDirectory "patch-generation.json"
$cliOutputPath = Join-Path $runDirectory "phase04-cli-output.json"
$cliErrorPath = Join-Path $runDirectory "phase04-cli-stderr.txt"
$summaryPath = Join-Path $runDirectory "phase04-live-summary.json"

$env:SCG_PHASE04_REPOSITORY = $repositoryPath
$env:SCG_PHASE04_BASE_REF = $resolvedBaseRef
$env:SCG_PHASE04_PATCH_PATH = $patchPath

$generator = @'
from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess
from pathlib import Path

repository = Path(os.environ["SCG_PHASE04_REPOSITORY"])
base_ref = os.environ["SCG_PHASE04_BASE_REF"]
patch_path = Path(os.environ["SCG_PHASE04_PATCH_PATH"])

shown = subprocess.run(
    ["git", "-C", str(repository), "show", f"{base_ref}:shipping.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=False,
)
if shown.returncode != 0:
    raise SystemExit("Could not read shipping.py from the immutable base ref.")

# Decode as plain UTF-8, not utf-8-sig, so an existing BOM remains in the first
# context line and git apply can match the base file byte-for-byte.
original = shown.stdout.decode("utf-8")
old_constant = "FREE_SHIPPING_THRESHOLD_CENTS = 5_000\n"
old_return = "    return 700\n"
if old_constant not in original or old_return not in original:
    raise SystemExit(
        "The controlled candidate expects the baseline shipping.py threshold and 700-cent return. "
        "No patch was written because the immutable base differs."
    )

modified = original.replace(
    old_constant,
    old_constant + "STANDARD_SHIPPING_CENTS = 700\n",
    1,
).replace(old_return, "    return STANDARD_SHIPPING_CENTS\n", 1)

shipping_diff = "diff --git a/shipping.py b/shipping.py\n" + "".join(
    difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile="a/shipping.py",
        tofile="b/shipping.py",
    )
)

test_content = """from shipping import (
    FREE_SHIPPING_THRESHOLD_CENTS,
    STANDARD_SHIPPING_CENTS,
    calculate_shipping,
)


def test_shipping_uses_named_standard_rate_below_threshold() -> None:
    assert calculate_shipping(FREE_SHIPPING_THRESHOLD_CENTS - 1) == STANDARD_SHIPPING_CENTS


def test_shipping_is_free_at_threshold() -> None:
    assert calculate_shipping(FREE_SHIPPING_THRESHOLD_CENTS) == 0
"""

test_diff = (
    "diff --git a/agent_solution/tests/test_shipping.py b/agent_solution/tests/test_shipping.py\n"
    "new file mode 100644\n"
    + "".join(
        difflib.unified_diff(
            [],
            test_content.splitlines(keepends=True),
            fromfile="/dev/null",
            tofile="b/agent_solution/tests/test_shipping.py",
        )
    )
)

patch = shipping_diff + test_diff
patch_path.write_text(patch, encoding="utf-8", newline="\n")
print(
    json.dumps(
        {
            "base_ref": base_ref,
            "patch_path": str(patch_path),
            "patch_sha256": hashlib.sha256(patch.encode("utf-8")).hexdigest(),
            "changed_paths": ["shipping.py", "agent_solution/tests/test_shipping.py"],
        },
        ensure_ascii=False,
    )
)
'@

try {
    $generatorLines = $generator | & $python -
    $generatorExitCode = $LASTEXITCODE
    [System.IO.File]::WriteAllText(
        $generatorOutputPath,
        ((@($generatorLines) -join "`n") + "`n"),
        $Utf8NoBom
    )
    if ($generatorExitCode -ne 0) {
        throw "Candidate patch generation failed. See: $generatorOutputPath"
    }

    & $python -m agent_solution validate-patch `
        --repository $repositoryPath `
        --patch-file $patchPath `
        --base-ref $resolvedBaseRef `
        --profile standard `
        --allow-path shipping.py `
        --allow-path agent_solution/tests/test_shipping.py `
        --artifact-dir $runDirectory `
        1> $cliOutputPath 2> $cliErrorPath
    $phase04ExitCode = $LASTEXITCODE

    # Windows PowerShell redirection writes UTF-16LE. Canonicalize emitted text
    # before parsing or preserving it as a machine-readable artifact.
    $cliOutputText = if (Test-Path -LiteralPath $cliOutputPath) {
        Get-Content -LiteralPath $cliOutputPath -Raw
    } else {
        ""
    }
    [System.IO.File]::WriteAllText($cliOutputPath, $cliOutputText, $Utf8NoBom)
    $cliErrorText = if (Test-Path -LiteralPath $cliErrorPath) {
        Get-Content -LiteralPath $cliErrorPath -Raw
    } else {
        ""
    }
    [System.IO.File]::WriteAllText($cliErrorPath, $cliErrorText, $Utf8NoBom)

    $result = $cliOutputText | ConvertFrom-Json
    $afterStatus = Get-GitStatusSnapshot -RepositoryPath $repositoryPath
    $sourceUnchanged = $beforeStatus -ceq $afterStatus

    $summary = [ordered]@{
        phase = "phase04-live"
        base_ref = $resolvedBaseRef
        status = $result.status
        cli_exit_code = $phase04ExitCode
        validation_artifact = $result.artifact_path
        source_checkout_unchanged = $sourceUnchanged
        command_results = @($result.command_results | ForEach-Object {
            [ordered]@{
                name = $_.name
                exit_code = $_.exit_code
                timed_out = $_.timed_out
                passed = $_.passed
            }
        })
    }
    $summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding utf8

    if (-not $sourceUnchanged) {
        throw "Source checkout status changed during Phase 04. Stop and inspect: $summaryPath"
    }
    if ($phase04ExitCode -ne 0 -or $result.status -ne "VALIDATED") {
        throw "Phase 04 did not validate the candidate. See: $cliOutputPath and $cliErrorPath"
    }
    if (@($result.command_results | Where-Object { -not $_.passed }).Count -ne 0) {
        throw "Phase 04 reported a non-passing command despite VALIDATED. See: $summaryPath"
    }

    Write-Host "[PASS] Phase 04 live validation" -ForegroundColor Green
    Write-Host "  status                   : $($result.status)"
    Write-Host "  source checkout unchanged : $sourceUnchanged"
    Write-Host "  validation artifact      : $($result.artifact_path)"
    Write-Host "  summary                  : $summaryPath"
    Write-Host "  patch                    : $patchPath"
}
finally {
    Remove-Item Env:\SCG_PHASE04_REPOSITORY -ErrorAction SilentlyContinue
    Remove-Item Env:\SCG_PHASE04_BASE_REF -ErrorAction SilentlyContinue
    Remove-Item Env:\SCG_PHASE04_PATCH_PATH -ErrorAction SilentlyContinue
}
