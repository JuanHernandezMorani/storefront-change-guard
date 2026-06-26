[CmdletBinding()]
param(
    [string]$Repository = (Split-Path -Parent $PSScriptRoot),
    [string]$LlamaCli = "",
    [string]$Model = "",
    [string]$ArtifactRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (!(Test-Path -LiteralPath $Repository -PathType Container)) {
    throw "Repository not found: $Repository"
}
$Repository = (Get-Item -LiteralPath $Repository).FullName
Set-Location $Repository

if ([string]::IsNullOrWhiteSpace($LlamaCli)) {
    $LlamaCli = $env:STORE_FRONT_GUARD_LLAMA_EXECUTABLE
}
if ([string]::IsNullOrWhiteSpace($Model)) {
    $Model = Join-Path $Repository "agent_solution\model\Qwen3.5-9B-UD-IQ3_XXS.gguf"
}

$Python = Join-Path $Repository ".venv\Scripts\python.exe"
if (!(Test-Path -LiteralPath $Python -PathType Leaf)) {
    $Python = "python"
}

foreach ($entry in @(
    @{ Label = "Python"; Path = $Python },
    @{ Label = "llama-cli"; Path = $LlamaCli },
    @{ Label = "Selected model"; Path = $Model }
)) {
    if ([string]::IsNullOrWhiteSpace($entry.Path) -or !(Test-Path -LiteralPath $entry.Path -PathType Leaf)) {
        throw "$($entry.Label) not found. Pass -$($entry.Label.Replace('-', '')) explicitly or configure the documented local path."
    }
}

$env:STORE_FRONT_GUARD_LLAMA_EXECUTABLE = $LlamaCli
$env:STORE_FRONT_GUARD_MODEL_PATH = $Model

if ([string]::IsNullOrWhiteSpace($ArtifactRoot)) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $ArtifactRoot = Join-Path $Repository "artifacts\phase03-live\run-$timestamp"
}
New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null

function Invoke-Phase03Gate {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Request,
        [Parameter(Mandatory = $true)][string]$Language,
        [Parameter(Mandatory = $true)][string]$StateDir,
        [Parameter(Mandatory = $true)][string]$ExpectedStatus,
        [bool]$ExpectCacheHit = $false,
        [bool]$ExpectModel = $true
    )

    $gateDir = Join-Path $ArtifactRoot $Name
    New-Item -ItemType Directory -Force -Path $gateDir, $StateDir | Out-Null
    $stdoutPath = Join-Path $gateDir "stdout.json"
    $stderrPath = Join-Path $gateDir "stderr.txt"

    & $Python -m agent_solution analyze `
        --request $Request `
        --repository $Repository `
        --language $Language `
        --format json `
        --state-dir $StateDir `
        1> $stdoutPath `
        2> $stderrPath

    $exitCode = $LASTEXITCODE
    $raw = if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw } else { "" }

    try {
        $result = $raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "$Name returned unreadable product JSON. stdout=$stdoutPath stderr=$stderrPath"
    }

    $passed = (
        $result.status -eq $ExpectedStatus -and
        ([bool]$result.cache_hit -eq $ExpectCacheHit)
    )

    if ($ExpectModel) {
        $passed = $passed -and ($result.model_id -eq "qwen3.5-9b-ud-iq3-xxs")
    }
    else {
        $passed = $passed -and [string]::IsNullOrWhiteSpace($result.model_id)
    }

    $label = if ($passed) { "PASS" } else { "FAIL" }
    Write-Host "[$label] $Name" -ForegroundColor $(if ($passed) { "Green" } else { "Red" })
    Write-Host "  status=$($result.status) cache_hit=$($result.cache_hit) model_id=$($result.model_id)"
    Write-Host "  stdout=$stdoutPath"
    Write-Host "  stderr=$stderrPath"

    if (!$passed) {
        throw "$Name did not meet its expected result. exit_code=$exitCode"
    }

    return $result
}

Write-Host "=== Phase 03 live gates ===" -ForegroundColor Cyan
Write-Host "Repository : $Repository"
Write-Host "Model      : $Model"
Write-Host "Artifacts  : $ArtifactRoot"
Write-Host ""

$gateAState = Join-Path $ArtifactRoot "state-a-b"
$gateCState = Join-Path $ArtifactRoot "state-c"
$gateDState = Join-Path $ArtifactRoot "state-d"

Invoke-Phase03Gate `
    -Name "gate-a" `
    -Request "Review shipping.py." `
    -Language "en" `
    -StateDir $gateAState `
    -ExpectedStatus "ANALYSIS_COMPLETED" `
    -ExpectCacheHit $false `
    -ExpectModel $true | Out-Null

Invoke-Phase03Gate `
    -Name "gate-b" `
    -Request "Review shipping.py." `
    -Language "en" `
    -StateDir $gateAState `
    -ExpectedStatus "ANALYSIS_CACHE_HIT" `
    -ExpectCacheHit $true `
    -ExpectModel $true | Out-Null

# ASCII Spanish avoids Windows PowerShell legacy decoding ambiguity while preserving the language test.
Invoke-Phase03Gate `
    -Name "gate-c" `
    -Request "Que hace calculate_shipping en shipping.py?" `
    -Language "es" `
    -StateDir $gateCState `
    -ExpectedStatus "ANALYSIS_COMPLETED" `
    -ExpectCacheHit $false `
    -ExpectModel $true | Out-Null

Invoke-Phase03Gate `
    -Name "gate-d" `
    -Request "Review definitely_missing_shipping_file.py." `
    -Language "en" `
    -StateDir $gateDState `
    -ExpectedStatus "INSUFFICIENT_EVIDENCE" `
    -ExpectCacheHit $false `
    -ExpectModel $false | Out-Null

Write-Host ""
Write-Host "All Phase 03 live gates passed." -ForegroundColor Green
Write-Host "Artifact root: $ArtifactRoot"
