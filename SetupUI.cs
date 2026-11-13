using System;
using System.IO;
using System.Diagnostics;
using System.Drawing;
using System.Windows.Forms;
using System.Collections.Generic;

public class SetupWindow : Form {
 readonly string root;
 readonly RichTextBox log = new RichTextBox();
 readonly Label status = new Label();
 readonly ProgressBar progress = new ProgressBar();
 readonly List<Button> installers = new List<Button>();
 Process running;
 bool busy;
 public SetupWindow(string directory) {
  root=directory; Text="LEVI Light | Setup & Launch"; Size=new Size(1040,760); MinimumSize=new Size(850,650);
  StartPosition=FormStartPosition.CenterScreen; BackColor=Color.FromArgb(15,18,25); ForeColor=Color.White;
  Font=new Font("Segoe UI",10);
  var layout=new TableLayoutPanel { Dock=DockStyle.Fill, Padding=new Padding(28), ColumnCount=1, RowCount=6 };
  layout.RowStyles.Add(new RowStyle(SizeType.Absolute,70)); layout.RowStyles.Add(new RowStyle(SizeType.Absolute,45));
  layout.RowStyles.Add(new RowStyle(SizeType.Absolute,350)); layout.RowStyles.Add(new RowStyle(SizeType.Absolute,32));
  layout.RowStyles.Add(new RowStyle(SizeType.Percent,100)); layout.RowStyles.Add(new RowStyle(SizeType.Absolute,35));
  Controls.Add(layout);
  layout.Controls.Add(new Label {Text="L E V I  LIGHT / SETUP", Font=new Font("Segoe UI",25,FontStyle.Bold), Dock=DockStyle.Fill},0,0);
  layout.Controls.Add(new Label {Text="Install your local assistant, choose your audio, then launch.",Dock=DockStyle.Fill,ForeColor=Color.Silver},0,1);
  var grid=new TableLayoutPanel {Dock=DockStyle.Fill,ColumnCount=3,RowCount=4};
  for(int i=0;i<3;i++) grid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,33.33f));
  for(int i=0;i<4;i++) grid.RowStyles.Add(new RowStyle(SizeType.Percent,25));
  layout.Controls.Add(grid,0,2);
  Add(grid,"01  INSTALL OLLAMA\n+ small CPU chat model",0,0,delegate { Run("Setup-Models.ps1","Installing Ollama and AI models",true); },true);
  Add(grid,"02  INSTALL HANDY\n+ Python, Piper and wake model",1,0,delegate { Run("Setup-Apps.ps1","Installing apps and speech components",true); },true);
  Add(grid,"03  CONFIGURE AUDIO\nMicrophone / speakers / headphones",2,0,delegate { if(HasPython()) Run("Configure-Audio.ps1","Audio configuration",false); else MessageBox.Show("Install apps first."); },true);
  Add(grid,"04  HANDY SETTINGS\nF2, speech model and connection",0,1,delegate { ShowHandy(); },false);
  Add(grid,"LAUNCH LEVI\nOpen the three service tabs",1,1,delegate { if(!HasPython()) {MessageBox.Show("Install apps first, then complete Handy settings.");return;} Run("Start-Levi.ps1","Starting Levi",false); },true);
  Add(grid,"SETUP GUIDE\nInstructions and troubleshooting",2,1,delegate {Process.Start("notepad.exe","\""+Path.Combine(root,"SETUP.md")+"\"");},false);
  Add(grid,"SETTINGS / API / MODELS",0,2,delegate { Run("Configure-Settings.ps1","Settings",false); },true);
  Add(grid,"REFRESH DESKTOP APPS",1,2,delegate { Run("Refresh-Apps.ps1","Desktop shortcuts",false); },true);
  Add(grid,"CONNECT SPOTIFY",2,2,delegate { if(HasPython()) Run("Connect-Spotify.ps1","Spotify authorization",false); else MessageBox.Show("Install apps first."); },true);
  Add(grid,"LIVE ON / OFF CONTROLS",0,3,delegate { Run("Control-Panel.ps1","Live controls",false); },true);
  progress.Dock=DockStyle.Fill; layout.Controls.Add(progress,0,3);
  log.Dock=DockStyle.Fill; log.ReadOnly=true; log.BackColor=Color.FromArgb(23,28,38); log.ForeColor=Color.FromArgb(180,210,230); log.Font=new Font("Consolas",9); layout.Controls.Add(log,0,4);
  status.Dock=DockStyle.Fill; status.Text="Ready. Start with steps 01 and 02. Internet is required for downloads."; layout.Controls.Add(status,0,5);
  Append("Installation folder: "+root);
  Append(HasPython()?"Python environment found. Setup can be rerun to repair missing components.":"Apps are not installed in this folder yet.");
  Append(File.Exists(Path.Combine(root,"voices","en_US-lessac-medium.onnx"))?"Piper Medium voice file found.":"Piper voice will download in step 02.");
  Append("Download output appears below. The activity bar does not estimate download percentage.");
  FormClosing += delegate(object sender,FormClosingEventArgs e) { if(busy) {e.Cancel=true; MessageBox.Show("Setup is still running. Wait for it to finish before closing this window.");} };
 }
 bool HasPython(){return File.Exists(Path.Combine(root,".venv","Scripts","python.exe"));}
 void Add(TableLayoutPanel grid,string text,int col,int row,EventHandler action,bool tracked){
  var b=new Button {Text=text,Dock=DockStyle.Fill,Margin=new Padding(5),FlatStyle=FlatStyle.Flat,BackColor=Color.FromArgb(29,42,60),ForeColor=Color.White,Cursor=Cursors.Hand};
  b.FlatAppearance.BorderColor=Color.FromArgb(55,110,150); b.Click+=action;grid.Controls.Add(b,col,row);if(tracked)installers.Add(b);
 }
 void Append(string text){if(IsDisposed)return;if(InvokeRequired){BeginInvoke(new Action<string>(Append),text);return;}log.AppendText(text+Environment.NewLine);log.SelectionStart=log.TextLength;log.ScrollToCaret();}
 void ShowHandy(){MessageBox.Show("In Handy:\n\n1. Download a transcription model.\n2. Select the same microphone as Levi.\n3. Assign F2 to transcription with post-processing.\n4. Set a Custom/OpenAI-compatible provider:\n\nBase URL: http://127.0.0.1:8765/v1\nModel: qwen3:0.6b\nAPI key, if required: local\n\nUse Handy's transcript insertion control in a prompt beginning Spoken question:.\n\nSee SETUP.md for the full instructions.","Handy configuration",MessageBoxButtons.OK,MessageBoxIcon.Information);}
 void Run(string script,string label,bool install){
  if(busy)return;
  string path=Path.Combine(root,script);
  if(!File.Exists(path)){MessageBox.Show("Missing script: "+path);return;}
  busy=true;foreach(var b in installers)b.Enabled=false;progress.Style=ProgressBarStyle.Marquee;status.Text=label+"...";Append("\n"+label);
  var info=new ProcessStartInfo("powershell.exe","-NoProfile -ExecutionPolicy Bypass -File \""+path+"\"");
  info.WorkingDirectory=root;info.UseShellExecute=false;info.CreateNoWindow=true;info.RedirectStandardOutput=true;info.RedirectStandardError=true;
  running=new Process {StartInfo=info,EnableRaisingEvents=true};
  running.OutputDataReceived+=delegate(object s,DataReceivedEventArgs e){if(e.Data!=null)Append(e.Data);};
  running.ErrorDataReceived+=delegate(object s,DataReceivedEventArgs e){if(e.Data!=null)Append(e.Data);};
  running.Exited+=delegate {var finished=running;int code=finished.ExitCode;BeginInvoke(new Action(delegate {busy=false;foreach(var b in installers)b.Enabled=true;progress.Style=ProgressBarStyle.Blocks;progress.Value=code==0?100:0;status.Text=code==0?label+" completed.":label+" failed. Read the log, fix the issue, and retry.";Append("Exit code: "+code);finished.Dispose();}));};
  try{running.Start();running.BeginOutputReadLine();running.BeginErrorReadLine();}catch(Exception e){busy=false;foreach(var b in installers)b.Enabled=true;progress.Style=ProgressBarStyle.Blocks;status.Text="Could not start setup.";Append(e.Message);running.Dispose();}
 }
 [STAThread] public static void Main(){Application.EnableVisualStyles();Application.Run(new SetupWindow(AppDomain.CurrentDomain.BaseDirectory));}
}
