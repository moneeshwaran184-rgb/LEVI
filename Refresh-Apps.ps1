. "$PSScriptRoot\common.ps1"
$apps=@{}
Get-ChildItem ([Environment]::GetFolderPath('Desktop')), "$env:PUBLIC\Desktop" -File -ErrorAction SilentlyContinue | Where-Object Extension -eq '.lnk' | ForEach-Object { $apps[$_.BaseName.ToLowerInvariant()]=$_.FullName }
$apps | ConvertTo-Json | Set-Content -Encoding UTF8 "$PSScriptRoot\desktop_apps.json"
Write-Host 'Desktop app shortcuts refreshed.'
