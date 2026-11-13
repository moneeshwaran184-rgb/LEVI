$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type -Path "$PSScriptRoot\SetupUI.cs" -ReferencedAssemblies System.Windows.Forms,System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
[System.Windows.Forms.Application]::Run([SetupWindow]::new($PSScriptRoot))
