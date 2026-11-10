. "$PSScriptRoot\common.ps1"
$csc = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $csc)) { throw 'The Windows .NET Framework C# compiler is required.' }
Run-Checked $csc @('/nologo','/target:exe','/out:LEVI.exe','Launcher.cs')
Copy-Item LEVI.exe 1-Setup-Models.exe -Force
Copy-Item LEVI.exe 2-Setup-Apps.exe -Force

Copy-Item LEVI.exe 'Configure Audio.exe' -Force
Run-Checked $csc @('/nologo','/target:winexe','/reference:System.Windows.Forms.dll','/reference:System.Drawing.dll','/out:LEVI Setup.exe','SetupUI.cs')
