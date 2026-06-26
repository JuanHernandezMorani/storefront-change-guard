param(
    [ValidateSet("all", "phase00", "phase02", "phase03", "phase04", "phase05")]
    [string]$Phase = "all",
    [switch]$NoHygiene,
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

$Arguments = @((Join-Path $PSScriptRoot "run_phase_validation.py"), "--phase", $Phase)
if ($NoHygiene) { $Arguments += "--no-hygiene" }
if ($Json) { $Arguments += "--json" }

& $Python @Arguments
exit $LASTEXITCODE
