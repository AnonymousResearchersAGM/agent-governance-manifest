[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$ParticipantId,
    [switch]$Resume
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
    "--task", "ALL",
    "--package-root", $PSScriptRoot
)
if ($Resume) {
    $Arguments += "--resume"
}

& $Python @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "P92 session stopped with an error. Records were not overwritten."
}
