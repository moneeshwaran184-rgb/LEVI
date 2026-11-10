. "$PSScriptRoot\common.ps1"
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Install-App 'Ollama.Ollama' }
$ollama = (Get-Command ollama -ErrorAction Stop).Source
try { Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null } catch {
    Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
    $ready = $false
    for ($i=0; $i -lt 30; $i++) {
        try { Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null; $ready=$true; break } catch { Start-Sleep 1 }
    }
    if (-not $ready) { throw 'Ollama did not start. Open Ollama and rerun this step.' }
}
Run-Checked $ollama @('pull','qwen3:4b-instruct')
Run-Checked $ollama @('pull','qwen3-vl:8b-instruct')
Write-Host 'Ollama and both models are ready. Run 2-Setup-Apps.exe next.'
