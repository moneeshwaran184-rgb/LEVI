using System;
using System.Diagnostics;
using System.IO;
class Launcher {
 [STAThread] static void Main(string[] args) {
  string root = AppDomain.CurrentDomain.BaseDirectory;
  string name = Path.GetFileNameWithoutExtension(Environment.GetCommandLineArgs()[0]);
  string script = name.StartsWith("1-") ? "Setup-Models.ps1" : name.StartsWith("2-") ? "Setup-Apps.ps1" : name.Contains("Settings") ? "Configure-Settings.ps1" : name.StartsWith("Configure") ? "Configure-Audio.ps1" : "Start-Levi.ps1";
  if (args.Length > 0 && args[0] == "--check") { Console.WriteLine(File.Exists(Path.Combine(root, script)) ? "Launcher OK" : "Missing script"); return; }
  var p = new ProcessStartInfo("powershell.exe", "-NoProfile -ExecutionPolicy Bypass -NoExit -File \"" + Path.Combine(root, script) + "\"");
  p.WorkingDirectory = root; p.UseShellExecute = true; Process.Start(p);
 }
}
