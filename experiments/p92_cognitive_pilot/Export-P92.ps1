[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ParticipantId
)

$ErrorActionPreference = "Stop"
& python (Join-Path $PSScriptRoot "scripts\export_p92_results.py") `
    --package-root $PSScriptRoot `
    --participant-id $ParticipantId
if ($LASTEXITCODE -ne 0) {
    throw "P92 result export failed."
}
