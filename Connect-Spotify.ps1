. "$PSScriptRoot\common.ps1"
Read-Settings
if (-not $env:SPOTIFY_CLIENT_ID) { throw 'Set SPOTIFY_CLIENT_ID in config.local.json first. See SETUP.md.' }
Run-Checked "$PSScriptRoot\.venv\Scripts\python.exe" @("$PSScriptRoot\spotify_control.py")
