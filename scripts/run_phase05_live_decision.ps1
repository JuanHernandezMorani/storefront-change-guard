<#
.SYNOPSIS
Runs the deterministic Phase 05 readiness decision from completed Phase 03 and Phase 04 artifacts.

.DESCRIPTION
Materializes canonical UTF-8 (no BOM) JSON copies of the supplied artifacts before invoking
`python -m agent_solution readiness`. This prevents Windows PowerShell UTF-16 redirection
artifacts from being passed directly to a Python JSON loader that requires UTF-8.

The script never starts a model, never applies a patch, and never modifies tracked source files.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Repository,

    [Parameter(Mandatory)]
    [string]$AnalysisArtifact,

    [Parameter(Mandatory)]
    [string]$PatchValidationArtifact,

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

function Read-TextWithBomDetection {
    param([Parameter(Mandatory)][string]$Path)

    $reader = New-Object System.IO.StreamReader($Path, $true)
    try {
        return $reader.ReadToEnd()
    }
    finally {
        $reader.Dispose()
    }
}

function Get-JsonObject {
    param([Parameter(Mandatory)][string]$Path)

    try {
        $raw = Read-TextWithBomDetection -Path $Path
        $value = $raw | ConvertFrom-Json
    }
    catch {
        throw "Could not parse JSON artifact '$Path': $($_.Exception.Message)"
    }
    if ($null -eq $value) {
        throw "JSON artifact '$Path' is empty or null."
    }
    return $value
}

function Write-CanonicalJsonCopy {
    param(
        [Parameter(Mandatory)][string]$SourcePath,
        [Parameter(Mandatory)][string]$DestinationPath
    )

    $raw = Read-TextWithBomDetection -Path $SourcePath
    try {
        $parsed = $raw | ConvertFrom-Json
    }
    catch {
        throw "Cannot canonicalize invalid JSON artifact '$SourcePath': $($_.Exception.Message)"
    }
    if ($null -eq $parsed) {
        throw "Cannot canonicalize empty JSON artifact '$SourcePath'."
    }

    # Preserve semantic JSON while making the byte encoding explicit for the Python CLI.
    if ($raw.Length -gt 0 -and [int][char]$raw[0] -eq 0xFEFF) {
        $raw = $raw.Substring(1)
    }
    [System.IO.File]::WriteAllText($DestinationPath, $raw, $Utf8NoBom)
}

function Get-OptionalPropertyText {
    param(
        [Parameter(Mandatory)]$Object,
        [Parameter(Mandatory)][string]$Name
    )

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value) {
        return ""
    }
    return [string]$property.Value
}

function Assert-InputArtifacts {
    param(
        [Parameter(Mandatory)]$Analysis,
        [Parameter(Mandatory)]$Validation
    )

    if ($Analysis.status -notin @("ANALYSIS_COMPLETED", "ANALYSIS_CACHE_HIT")) {
        throw "Phase 03 artifact is not a completed analysis. status=$($Analysis.status)"
    }
    if ([string]::IsNullOrWhiteSpace([string]$Analysis.evidence_bundle_sha256)) {
        throw "Phase 03 artifact has no evidence_bundle_sha256."
    }
    if ([string]::IsNullOrWhiteSpace([string]$Analysis.model_id)) {
        throw "Phase 03 artifact has no runtime model identity."
    }
    if ($Validation.status -ne "VALIDATED") {
        throw "Phase 04 artifact is not VALIDATED. status=$($Validation.status)"
    }
    $commands = @($Validation.command_results)
    if ($commands.Count -eq 0) {
        throw "Phase 04 artifact contains no command_results."
    }
    $failed = @($commands | Where-Object { $_.exit_code -ne 0 -or $_.timed_out -eq $true })
    if ($failed.Count -ne 0) {
        $names = (($failed | ForEach-Object { $_.name }) -join ", ")
        throw "Phase 04 artifact contains a failed or timed-out command: $names"
    }
}

$repositoryItem = Get-Item -LiteralPath $Repository -ErrorAction Stop
if (-not $repositoryItem.PSIsContainer) {
    throw "Repository must be a directory: $Repository"
}
$repositoryPath = $repositoryItem.FullName

$analysisItem = Get-Item -LiteralPath $AnalysisArtifact -ErrorAction Stop
$validationItem = Get-Item -LiteralPath $PatchValidationArtifact -ErrorAction Stop
if ($analysisItem.PSIsContainer -or $validationItem.PSIsContainer) {
    throw "AnalysisArtifact and PatchValidationArtifact must be JSON files."
}

$analysis = Get-JsonObject -Path $analysisItem.FullName
$validation = Get-JsonObject -Path $validationItem.FullName
Assert-InputArtifacts -Analysis $analysis -Validation $validation

$python = Join-Path $repositoryPath ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $python = "python"
}

$root = if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) {
    Join-Path $repositoryPath "artifacts\phase05-live"
} else {
    $ArtifactRoot
}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDirectory = Join-Path $root "run-$timestamp"
$inputsDirectory = Join-Path $runDirectory "inputs"
New-Item -ItemType Directory -Path $inputsDirectory -Force | Out-Null

$beforeStatus = Get-GitStatusSnapshot -RepositoryPath $repositoryPath
$analysisCopy = Join-Path $inputsDirectory "phase03-analysis.utf8.json"
$validationCopy = Join-Path $inputsDirectory "phase04-validation.utf8.json"
Write-CanonicalJsonCopy -SourcePath $analysisItem.FullName -DestinationPath $analysisCopy
Write-CanonicalJsonCopy -SourcePath $validationItem.FullName -DestinationPath $validationCopy

$cliOutputPath = Join-Path $runDirectory "phase05-cli-output.json"
$cliErrorPath = Join-Path $runDirectory "phase05-cli-stderr.txt"
$summaryPath = Join-Path $runDirectory "phase05-live-summary.json"

$cliLines = & $python -m agent_solution readiness `
    --analysis-artifact $analysisCopy `
    --patch-validation-artifact $validationCopy `
    --artifact-dir $runDirectory `
    2> $cliErrorPath
$phase05ExitCode = $LASTEXITCODE
$cliText = (@($cliLines) -join "`n")
[System.IO.File]::WriteAllText($cliOutputPath, $cliText + "`n", $Utf8NoBom)

$result = Get-JsonObject -Path $cliOutputPath
$afterStatus = Get-GitStatusSnapshot -RepositoryPath $repositoryPath
$sourceUnchanged = $beforeStatus -ceq $afterStatus

$reasonCodes = @()
$reasonsProperty = $result.PSObject.Properties["reasons"]
if ($null -ne $reasonsProperty -and $null -ne $reasonsProperty.Value) {
    $reasonCodes = @($reasonsProperty.Value | ForEach-Object { $_.code })
}

$summary = [ordered]@{
    phase = "phase05-live"
    status = Get-OptionalPropertyText -Object $result -Name "status"
    cli_exit_code = $phase05ExitCode
    policy_version = Get-OptionalPropertyText -Object $result -Name "policy_version"
    decision_artifact = Get-OptionalPropertyText -Object $result -Name "artifact_path"
    analysis_input = [ordered]@{
        source_path = $analysisItem.FullName
        canonical_utf8_copy = $analysisCopy
        status = [string]$analysis.status
        model_id = [string]$analysis.model_id
        evidence_bundle_sha256 = [string]$analysis.evidence_bundle_sha256
    }
    patch_validation_input = [ordered]@{
        source_path = $validationItem.FullName
        canonical_utf8_copy = $validationCopy
        status = [string]$validation.status
        run_id = Get-OptionalPropertyText -Object $validation -Name "run_id"
        command_count = @($validation.command_results).Count
    }
    decision_reason_codes = $reasonCodes
    source_checkout_unchanged = $sourceUnchanged
    model_invocation = "none; deterministic readiness policy only"
}
[System.IO.File]::WriteAllText(
    $summaryPath,
    (($summary | ConvertTo-Json -Depth 8) + "`n"),
    $Utf8NoBom
)

if (-not $sourceUnchanged) {
    throw "Source checkout status changed during Phase 05. Stop and inspect: $summaryPath"
}
if ($phase05ExitCode -ne 0 -or $result.status -ne "READY") {
    throw "Phase 05 did not reach READY. See: $cliOutputPath and $cliErrorPath"
}
if ($reasonCodes -notcontains "ALL_REQUIRED_GATES_PASSED") {
    throw "Phase 05 returned READY without ALL_REQUIRED_GATES_PASSED. See: $summaryPath"
}
if (-not (Test-Path -LiteralPath $result.artifact_path -PathType Leaf)) {
    throw "Phase 05 decision artifact was not created: $($result.artifact_path)"
}

Write-Host "[PASS] Phase 05 live readiness decision" -ForegroundColor Green
Write-Host "  status                    : $($result.status)"
Write-Host "  policy version            : $($result.policy_version)"
Write-Host "  source checkout unchanged : $sourceUnchanged"
Write-Host "  decision artifact         : $($result.artifact_path)"
Write-Host "  summary                   : $summaryPath"
Write-Host "  model invocation          : none (deterministic policy)"
