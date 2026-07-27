[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
& python (Join-Path $PSScriptRoot "scripts\stop_p92.py") `
    --package-root $PSScriptRoot
if ($LASTEXITCODE -ne 0) {
    throw "P92 process cleanup failed."
}
