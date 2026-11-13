. "$PSScriptRoot\common.ps1"
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$dir=Join-Path $PSScriptRoot 'data\controls'; New-Item -ItemType Directory -Force $dir | Out-Null
$form=New-Object Windows.Forms.Form; $form.Text='LEVI Live On/Off'; $form.Size=New-Object Drawing.Size(570,440); $form.StartPosition='CenterScreen'
$status=New-Object Windows.Forms.Label; $status.Location=New-Object Drawing.Point(16,12);$status.Size=New-Object Drawing.Size(520,40);$status.Text='Checking Levi...';$form.Controls.Add($status)
function Send-Control($feature,$enabled){
 $stamp=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000.0
 $path=Join-Path $dir ('command-'+[guid]::NewGuid().ToString()+'.json')
 @{feature=$feature;enabled=$enabled;created=$stamp}|ConvertTo-Json|Set-Content -Encoding UTF8 ($path+'.tmp')
 Move-Item -LiteralPath ($path+'.tmp') -Destination $path
}
$labels=@{};$buttons=@();$y=60
foreach($feature in @('wake','speech','actions','vision','cloud')){
 $label=New-Object Windows.Forms.Label;$label.Text=$feature;$label.Location=New-Object Drawing.Point(16,$y);$label.Size=New-Object Drawing.Size(280,30);$form.Controls.Add($label);$labels[$feature]=$label
 foreach($choice in @('On','Off')){
  $button=New-Object Windows.Forms.Button;$button.Text=$choice;$button.Tag=@($feature,($choice -eq 'On'));$x=if($choice -eq 'On'){310}else{410};$button.Location=New-Object Drawing.Point($x,$y);$button.Width=85
  $button.Add_Click({Send-Control $this.Tag[0] $this.Tag[1]});$form.Controls.Add($button);$buttons+=$button
 };$y+=44
}
foreach($item in @(@('Stop speaking','stop'),@('Shut down Levi','sleep'))){
 $b=New-Object Windows.Forms.Button;$b.Text=$item[0];$b.Tag=$item[1];$b.Location=New-Object Drawing.Point(16,$y);$b.Width=220;$b.Add_Click({Send-Control $this.Tag $false});$form.Controls.Add($b);$buttons+=$b;$y+=35
}
$timer=New-Object Windows.Forms.Timer;$timer.Interval=700
$timer.Add_Tick({
 try {
  $s=Get-Content (Join-Path $dir 'status.json') -Raw -ErrorAction Stop|ConvertFrom-Json
  $age=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000.0-$s.updated
  if($age -gt 3){throw 'offline'}
  $status.Text='Levi running. Changes apply now; startup defaults are in Settings.'
  foreach($f in $labels.Keys){$value=if($s.$f){'ON'}else{'OFF'};$labels[$f].Text="$f : $value"}
  if(-not $s.cloud_ready){$labels['cloud'].Text+=' (key missing or disabled)'}
  foreach($b in $buttons){$b.Enabled=$true}
 }catch{$status.Text='Levi is not running. Close this panel and click Launch Levi.';foreach($b in $buttons){$b.Enabled=$false}}
});$timer.Start();$form.Add_FormClosed({$timer.Stop();$timer.Dispose()});[void]$form.ShowDialog()
