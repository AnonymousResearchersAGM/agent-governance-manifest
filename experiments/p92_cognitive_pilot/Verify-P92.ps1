[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

& $Python (Join-Path $PSScriptRoot "scripts\verify_p92_package.py") `
    --repo-root $RepoRoot `
    --package-root $PSScriptRoot
if ($LASTEXITCODE -ne 0) {
    throw "P92 verification failed. The pilot was not started."
}
