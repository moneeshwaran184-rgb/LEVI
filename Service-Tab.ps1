param([ValidateSet('Ollama','Piper','Bridge')]$Service)
. "$PSScriptRoot\common.ps1"
Read-Settings
$py = "$PSScriptRoot\.venv\Scripts\python.exe"
function Up($url) { try { Invoke-RestMethod $url -TimeoutSec 2 | Out-Null; return $true } catch { return $false } }
if ($Service -eq 'Ollama') {
    if (Up 'http://127.0.0.1:11434/api/tags') { Write-Host 'Ollama already running.' } else { & ollama serve }
} elseif ($Service -eq 'Piper') {
    if (Up 'http://127.0.0.1:5000/info') { Write-Host 'Piper already running.' } else {
        Run-Checked $py @('-m','piper.http_server','--host','127.0.0.1','-m','en_US-lessac-high','--data-dir',"$PSScriptRoot\voices")
    }
} else {
    if (-not (Test-Path $py)) { throw 'Run the two setup icons first.' }
    if (Up 'http://127.0.0.1:8765/health') { throw 'Another Levi bridge is already running. Close it first.' }
    foreach ($url in @('http://127.0.0.1:11434/api/tags','http://127.0.0.1:5000/info')) {
        $ready=$false
        for($i=0;$i -lt 60;$i++){ if(Up $url){$ready=$true;break}; Start-Sleep 1 }
        if(-not $ready){throw "Service unavailable: $url. Read its tab for errors."}
    }
    $handy = & $py -c 'from handy_screen_on_demand import handy_executable; print(handy_executable())'
    if(-not $handy -or $handy -eq 'None'){throw 'Set HANDY_EXE in config.local.json to your installed handy.exe.'}
    if(-not (Get-Process handy -ErrorAction SilentlyContinue)){Start-Process -FilePath $handy}
    Run-Checked $py @("$PSScriptRoot\handy_screen_on_demand.py")
}
