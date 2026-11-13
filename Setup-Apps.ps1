. "$PSScriptRoot\common.ps1"
$python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $python)) { Install-App 'Python.Python.3.12' }
if (-not (Test-Path $python)) {
    $python = & py -3.12 -c 'import sys; print(sys.executable)'
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $python)) { throw 'Python 3.12 was not found. Restart this setup after Python installation.' }
}
Install-App 'cjpais.Handy'
if (-not (Get-Command wt.exe -ErrorAction SilentlyContinue)) { Install-App 'Microsoft.WindowsTerminal' }
if (-not (Test-Path '.venv\Scripts\python.exe')) { Run-Checked $python @('-m','venv',"$PSScriptRoot\.venv") }
$py = "$PSScriptRoot\.venv\Scripts\python.exe"
Run-Checked $py @('-m','pip','install','-r',"$PSScriptRoot\requirements.txt")
New-Item -ItemType Directory -Force voices,wake_models,data | Out-Null
Run-Checked $py @('-m','piper.download_voices','--download-dir',"$PSScriptRoot\voices",'en_US-lessac-medium')
if (-not (Test-Path 'wake_models\vosk-model-small-en-us-0.15\am\final.mdl')) {
    Invoke-WebRequest 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip' -OutFile 'wake_models\wake.zip' -UseBasicParsing
    Expand-Archive 'wake_models\wake.zip' 'wake_models' -Force
    Remove-Item -LiteralPath "$PSScriptRoot\wake_models\wake.zip"
}
if (-not (Test-Path 'config.local.json')) { Copy-Item config.example.json config.local.json }
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'LEVI Light.lnk'))
$shortcut.TargetPath = "$PSScriptRoot\LEVI.exe"
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Save()
Start-Process notepad.exe -ArgumentList ('"'+$PSScriptRoot+'\SETUP.md"')
Write-Host 'Apps installed and Desktop LEVI shortcut created. Complete the Handy microphone/model/F2/provider settings in SETUP.md before starting.'
