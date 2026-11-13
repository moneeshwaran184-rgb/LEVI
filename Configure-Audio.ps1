. "$PSScriptRoot\common.ps1"
if (-not (Test-Path '.venv\Scripts\python.exe')) { throw 'Run 2-Setup-Apps.exe first.' }
Run-Checked "$PSScriptRoot\.venv\Scripts\python.exe" @("$PSScriptRoot\configure_audio.py")
