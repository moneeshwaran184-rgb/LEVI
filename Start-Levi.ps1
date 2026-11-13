. "$PSScriptRoot\common.ps1"
if (-not (Get-Command wt.exe -ErrorAction SilentlyContinue)) { throw 'Install Windows Terminal from Microsoft Store first.' }
& "$PSScriptRoot\Refresh-Apps.ps1"
$tab = Join-Path $PSScriptRoot 'Service-Tab.ps1'
& wt.exe -w LEVI-Light new-tab --title Ollama -d $PSScriptRoot powershell.exe -NoProfile -NoExit -ExecutionPolicy Bypass -File $tab Ollama `; new-tab --title Piper -d $PSScriptRoot powershell.exe -NoProfile -NoExit -ExecutionPolicy Bypass -File $tab Piper `; new-tab --title LEVI -d $PSScriptRoot powershell.exe -NoProfile -NoExit -ExecutionPolicy Bypass -File $tab Bridge
