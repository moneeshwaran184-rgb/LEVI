$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
function Run-Checked($Exe, $Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Exe failed with exit code $LASTEXITCODE. Correct the error and rerun setup." }
}
function Install-App($Id) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'Install Microsoft App Installer (winget), then rerun setup.' }
    & winget install --id $Id --exact --source winget --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) { throw "Installation of $Id failed: $LASTEXITCODE" }
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
}
function Read-Settings {
    if (-not (Test-Path "$PSScriptRoot\config.local.json")) { Copy-Item "$PSScriptRoot\config.example.json" "$PSScriptRoot\config.local.json" }
    $defaults = Get-Content "$PSScriptRoot\config.example.json" -Raw | ConvertFrom-Json
    foreach ($item in $defaults.PSObject.Properties) { [Environment]::SetEnvironmentVariable($item.Name,[string]$item.Value,'Process') }
    if (Test-Path "$PSScriptRoot\config.local.json") {
        $settings = Get-Content "$PSScriptRoot\config.local.json" -Raw | ConvertFrom-Json
        foreach ($item in $settings.PSObject.Properties) { [Environment]::SetEnvironmentVariable($item.Name,[string]$item.Value,'Process') }
    }
}
