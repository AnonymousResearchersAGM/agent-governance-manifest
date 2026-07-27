[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$ParticipantId,
    [Parameter(Mandatory = $true)]
    [ValidateSet("T0", "T1", "T2", "T3", "T4")]
    [string]$Task,
    [switch]$Resume,
    [switch]$TechnicalRerun
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "Verify-P92.ps1") -RepoRoot $RepoRoot

$ResolvedRepo = (Resolve-Path -LiteralPath $RepoRoot).Path
$Python = Join-Path $ResolvedRepo ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}
$Arguments = @(
    (Join-Path $PSScriptRoot "scripts\run_p92_session.py"),
    "--repo-root", $ResolvedRepo,
    "--participant-id", $ParticipantId,
    "--task", $Task,
    "--package-root", $PSScriptRoot
)
if ($Resume) {
    $Arguments += "--resume"
}
if ($TechnicalRerun) {
    $Arguments += "--technical-rerun"
}

& $Python @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "P92 task stopped with an error."
}
