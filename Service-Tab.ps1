param([ValidateSet('Ollama','Piper','Bridge')]$Service)
. "$PSScriptRoot\common.ps1"
Read-Settings
$py = "$PSScriptRoot\.venv\Scripts\python.exe"
$sleepMarker = "$PSScriptRoot\data\sleep.requested"
Remove-Item $sleepMarker -Force -ErrorAction SilentlyContinue
function Up($url) { try { Invoke-RestMethod $url -TimeoutSec 2 | Out-Null; return $true } catch { return $false } }
function Wait-ForSleep {
    while (-not (Test-Path $sleepMarker)) { Start-Sleep -Milliseconds 500 }
    Write-Host 'Levi is asleep. Closing this tab.'
    [Environment]::Exit(0)
}
if ($Service -eq 'Ollama') {
    if (Up 'http://127.0.0.1:11434/api/tags') {
        Write-Host 'Ollama already running.'
        Wait-ForSleep
    } else {
        $proc = Start-Process -FilePath 'ollama' -ArgumentList 'serve' -NoNewWindow -PassThru
        $watcher = Start-Job -ScriptBlock {
            param($marker, $servicePid)
            while (-not (Test-Path $marker)) { Start-Sleep -Milliseconds 500 }
            Stop-Process -Id $servicePid -Force -ErrorAction SilentlyContinue
        } -ArgumentList $sleepMarker, $proc.Id
        $proc.WaitForExit()
        Remove-Job $watcher -Force -ErrorAction SilentlyContinue
        if (Test-Path $sleepMarker) { Wait-ForSleep }
        if ($proc.ExitCode -ne 0) { throw "Ollama failed with exit code $($proc.ExitCode)." }
    }
} elseif ($Service -eq 'Piper') {
    if (Up 'http://127.0.0.1:5000/info') {
        Write-Host 'Piper already running.'
        Wait-ForSleep
    } else {
        try {
            Run-Checked $py @('-m','piper.http_server','--host','127.0.0.1','-m','en_US-lessac-medium','--data-dir',"$PSScriptRoot\voices")
        } catch {
            if (Test-Path $sleepMarker) { Wait-ForSleep }
            throw
        }
    }
} else {
    if (-not (Test-Path $py)) { throw 'Run the two setup icons first.' }
    if (Up 'http://127.0.0.1:8765/health') { throw 'Another Levi bridge is already running. Close it first.' }
    foreach ($url in @('http://127.0.0.1:11434/api/tags','http://127.0.0.1:5000/info')) {
        $ready=$false
        for($i=0;$i -lt 60;$i++){ if(Up $url){$ready=$true;break}; Start-Sleep 1 }
        if(-not $ready){throw "Service unavailable: $url. Read its tab for errors."}
    }
    $handy = & $py -c 'from handy_screen_on_demand import handy_executable; print(handy_executable() or str())'
    if(-not $handy){throw 'Set HANDY_EXE in config.local.json to your installed handy.exe.'}
    if(-not (Get-Process handy -ErrorAction SilentlyContinue)){Start-Process -FilePath $handy}
    while ($true) {
        & $py "$PSScriptRoot\handy_screen_on_demand.py"
        $code = $LASTEXITCODE
        if (Test-Path $sleepMarker) {
            Write-Host 'Levi is asleep. Closing this tab.'
            [Environment]::Exit(0)
        }
        if ($code -in 0, 130) { break }
        if (Up 'http://127.0.0.1:8765/health') { break }
        Write-Host "Levi bridge stopped unexpectedly (exit $code). Restarting in 5 seconds; press Ctrl+C to stop."
        Start-Sleep -Seconds 5
    }
}

