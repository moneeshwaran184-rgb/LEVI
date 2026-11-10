# LEVI setup details

## Requirements and downloads

Windows 10/11 x64, Windows Terminal, Microsoft App Installer (winget), a microphone and speakers/headphones. Allow several GB of disk space for Ollama models and dependencies. A GPU helps; vision is substantially heavier than ordinary chat. Setup downloads from winget publishers, PyPI, Piper's voice host and alphacephei.com. Download times depend on your connection.

Run 1-Setup-Models.exe, then 2-Setup-Apps.exe. Installer prompts may request Windows approval. If setup fails, read the error and rerun the same step after fixing it. Do not run downloaded setup code without reviewing its source. No credentials are required for local voice/chat.

## Required Handy first-run configuration

Open Handy, complete its onboarding and download a transcription model from its model selector. Choose a smaller supported model first if latency matters. This model is managed by Handy and requires first-run selection; the setup script does not silently edit Handy's internal configuration.

Select your microphone in Handy. Set its transcription-with-post-processing shortcut to **F2**. Enable a Custom/OpenAI-compatible post-processing provider with base URL **http://127.0.0.1:8765/v1**, model **qwen3:4b-instruct**. If an API-key field is mandatory, use `local` (the loopback bridge does not require a cloud key). Choose a prompt that includes your transcription as `Spoken question: <transcription>` using Handy's supported transcript insertion control. Speak a short question with F2 before enabling hands-free use.

## Audio configuration

Run Configure Audio.exe after app setup. Choose a microphone and speaker/headphone output, play the test tone, check microphone levels, and Save. Select the SAME microphone in Handy because Handy performs transcription independently. Restart Levi after changing settings. Reopen the configuration window after connecting new devices. Windows default follows the OS device. The wake MP3 follows Windows default output; use Windows Settings > System > Sound to choose its output.

## Launch and shutdown

LEVI.exe opens three tabs in a single named Windows Terminal window: Ollama, Piper, LEVI. Existing Ollama/Piper services are detected and reused; their tab reports that they already run. The bridge tab waits for them to become ready. An already-running Levi bridge produces a clear error instead of starting a duplicate. Close the old D: installation before running E: LEVI because both use the same ports (11434, 5000, 8765).

Use Ctrl+C in each service tab to stop a service launched there. An Ollama tray service that was already running must be closed from its tray menu if desired. Setup creates a Desktop shortcut pointing to LEVI.exe; moving the folder afterwards requires rerunning setup to update that shortcut.

## Optional Spotify

Create your own Spotify developer app with Web API enabled and redirect URI `http://127.0.0.1:8888/callback`. Add your own client ID under SPOTIFY_CLIENT_ID in config.local.json, then run Connect-Spotify.ps1 with PowerShell. Sign in and authorize the requested playback permissions. Playback API access requires an eligible Spotify account (typically Premium) and developer-app access. Open the desktop player and play something once so it is discoverable. No client secret is shipped or needed by this PKCE flow. Tokens stay in data/ and are tied to your Windows account.

## Configuration

Copy config.example.json to config.local.json if absent. This private JSON file contains environment overrides read by each service tab. HANDY_EXE sets a nonstandard Handy installation path. HANDY_MICROPHONE and HANDY_SPEAKER store device names. HANDY_MODEL_KEEP_ALIVE defaults to 45s. HANDY_WAKE_ENABLED / HANDY_ACTIONS_ENABLED / HANDY_MEMORY_ENABLED can be set to 0. Restart after edits. Vision can be turned off using `vision off` in the LEVI tab.

## Build the launchers

Run `powershell -NoProfile -ExecutionPolicy Bypass -File Build.ps1` in this folder on Windows with the .NET Framework C# compiler installed. It builds LEVI.exe and copies it to the two setup launcher names and Configure Audio.exe. These unsigned launchers use their own folder to find scripts; keep the entire folder together. Windows may show a reputation prompt for unsigned downloads.

## Troubleshooting

- No mic: verify Windows microphone permission, audio configuration and Handy's microphone selection.
- No speech: inspect Piper tab and test selected output. Reconnect headset and refresh choices.
- Slow first answer: initial Ollama loading costs time; repeated answers within 45 seconds reuse the text model. Vision is slower. There is no guaranteed instant response.
- Follow-up misses speech: wait for wake sound; no speech cancels after nine seconds. Use F2 fallback.
- Port in use: close other Levi installation/services before retrying.
- Python missing: rerun app setup after reopening the setup terminal; avoid the Microsoft Store Python placeholder.
- Install failed: setup stops on errors; review the failing command and rerun. Models are not bundled in GitHub.

On the build machine, Application Control blocked executing the unsigned EXEs. Compilation succeeded, but EXE launch validation is incomplete. Script launchers (.cmd) are included for systems whose policy permits these scripts; do not disable your organization's application-control policy.

## Visual setup interface
Open LEVI Setup.exe (or Open_Setup.cmd where allowed). Use Install Ollama first, then Install Handy. Configure Audio opens the device selectors after dependencies are installed. Handy Settings shows the required manual settings. Launch LEVI opens the three service tabs. Downloads run in background child processes; progress output and errors appear in the log. Closing the dashboard is blocked while an operation runs so installation is not accidentally abandoned. Installers may still display their own Windows permission dialogs.
