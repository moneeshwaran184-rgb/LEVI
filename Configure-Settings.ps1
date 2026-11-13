. "$PSScriptRoot\common.ps1"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Read-Settings
$config=Get-Content "$PSScriptRoot\config.local.json" -Raw | ConvertFrom-Json
$form=New-Object Windows.Forms.Form
$form.Text='LEVI Light Settings'; $form.Size=New-Object Drawing.Size(820,740); $form.StartPosition='CenterScreen'
$panel=New-Object Windows.Forms.Panel; $panel.Dock='Fill'; $panel.AutoScroll=$true; $form.Controls.Add($panel)
$fields=@(
 @('HANDY_CHAT_MODEL','Local model (install after changing)'),
 @('HANDY_CPU_THREADS','CPU threads (1-16; default 4)'),
 @('HANDY_WAKE_SILENCE_SECONDS','Silence seconds (0.7-3; default 0.8)'),
 @('HANDY_MODEL_KEEP_ALIVE','Keep model loaded (for example 5m)'),
 @('HANDY_MICROPHONE','Microphone (blank = Windows default)'),
 @('HANDY_SPEAKER','Speaker/headphones (blank = Windows default)'),
 @('HANDY_OUTPUT_DIR','Save files folder (blank = Documents/LeviFiles)'),
 @('HANDY_EXE','Handy.exe path (blank = auto detect)'),
 @('HANDY_CLOUD_PROVIDER','API provider: gemini or openai-compatible'),
 @('HANDY_CLOUD_URL','Full API endpoint URL'),
 @('HANDY_CLOUD_API_KEY','API key (private; stored only on this PC)'),
 @('HANDY_CLOUD_MODEL','API model ID from your provider'),
 @('HANDY_CLOUD_MODELS','Fallback model IDs, comma separated'),
 @('SPOTIFY_CLIENT_ID','Spotify developer client ID'),
 @('VISION_MODEL','Optional vision model (install separately)'),
 @('HANDY_VISION_ENABLED','Vision at startup: 0 off / 1 on'),
 @('HANDY_WAKE_ENABLED','Wake at startup: 0 off / 1 on'),
 @('HANDY_ACTIONS_ENABLED','App actions at startup: 0 off / 1 on'),
 @('HANDY_MEMORY_ENABLED','Memory: 0 off / 1 on'),
 @('HANDY_CLOUD_ENABLED','API backup: 0 off / 1 on')
)
$controls=@{}; $y=12
foreach($field in $fields){
 $label=New-Object Windows.Forms.Label; $label.Text=$field[1]; $label.Location=New-Object Drawing.Point(12,$y); $label.Size=New-Object Drawing.Size(325,28); $panel.Controls.Add($label)
 $box=New-Object Windows.Forms.TextBox; $box.Location=New-Object Drawing.Point(340,$y); $box.Size=New-Object Drawing.Size(420,28); $box.Text=[string]$config.($field[0]); if($field[0] -eq 'HANDY_CLOUD_API_KEY'){$box.UseSystemPasswordChar=$true}; $panel.Controls.Add($box); $controls[$field[0]]=$box; $y+=42
}
$save=New-Object Windows.Forms.Button; $save.Text='Save settings'; $save.Location=New-Object Drawing.Point(340,$y); $save.Width=180; $panel.Controls.Add($save)
$save.Add_Click({
 try {
  $seconds=[double]::Parse($controls['HANDY_WAKE_SILENCE_SECONDS'].Text,[Globalization.CultureInfo]::InvariantCulture)
  $threads=[int]$controls['HANDY_CPU_THREADS'].Text
  if($seconds -lt 0.7 -or $seconds -gt 3 -or $threads -lt 1 -or $threads -gt 16){throw 'Silence must be 0.7-3 seconds and CPU threads 1-16.'}
  if($controls['HANDY_CLOUD_PROVIDER'].Text -notin @('gemini','openai-compatible')){throw 'Provider must be gemini or openai-compatible.'}
  if($controls['HANDY_CLOUD_URL'].Text -notmatch '^https://'){throw 'Use a full HTTPS API endpoint.'}
  foreach($key in $controls.Keys){ $config | Add-Member -NotePropertyName $key -NotePropertyValue $controls[$key].Text -Force }
  $temp="$PSScriptRoot\config.local.json.tmp"; $config | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $temp; Move-Item -LiteralPath $temp -Destination "$PSScriptRoot\config.local.json" -Force
  [Windows.Forms.MessageBox]::Show('Saved. Restart Levi. After changing the local model, run Install Ollama/models. Use Configure Audio for device lists and tests. Select the same microphone in Handy.')
 } catch { [Windows.Forms.MessageBox]::Show($_.Exception.Message) }
})
[void]$form.ShowDialog()
