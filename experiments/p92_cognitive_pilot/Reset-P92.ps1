[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("T0", "T1", "T2", "T3", "T4")]
    [string]$Task,
    [string]$RepoRoot,
    [switch]$ClearRecords
)

$ErrorActionPreference = "Stop"
$Python = "python"
if ($RepoRoot) {
    $ResolvedRepo = (Resolve-Path -LiteralPath $RepoRoot).Path
    $Candidate = Join-Path $ResolvedRepo ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $Candidate) {
        $Python = $Candidate
    }
}
$Arguments = @(
    (Join-Path $PSScriptRoot "scripts\reset_p92.py"),
    "--package-root", $PSScriptRoot,
    "--task", $Task
)
if ($RepoRoot) {
    $Arguments += @("--repo-root", $ResolvedRepo)
}
if ($ClearRecords) {
    Write-Warning "ClearRecords is a destructive debug-only action and must not be used in formal P92 running."
    $Confirmation = Read-Host "Type CLEAR RECORDS to confirm"
    if ($Confirmation -ne "CLEAR RECORDS") {
        throw "Record clearing cancelled."
    }
    $Arguments += @("--clear-records", "--confirm-clear", "CLEAR RECORDS")
}

& $Python @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "P92 reset failed."
}
