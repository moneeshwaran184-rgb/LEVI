# LEVI Light for Windows

Portable installer/source bundle for Windows 10/11 x64 Intel or AMD laptops. Run **LEVI Setup.exe** after extracting the whole ZIP to a writable folder. No Python is needed to open the setup window. Models and dependencies download during installation; this is not an offline installer.

## Laptop defaults
- qwen3:0.6b local chat, CPU-only, four threads; editable in Settings.
- Piper Lessac medium voice, Vosk local wake recognition, Handy transcription.
- Vision off by default. No NVIDIA GPU or CUDA required.
- Designed as a low-resource starting point for an Intel Core/Core Ultra laptop. Exact speed depends on RAM, cooling and transcription model; not benchmarked on your target laptop. The 0.6b model trades accuracy for speed.
- Use a small English transcription model in Handy. 8 GB RAM is a practical starting point; 16 GB gives more room for other apps.

## Setup window
1. SETTINGS / API / MODELS: choose model, CPU threads, API provider, endpoint, key, output folder, timing and startup switches.
2. INSTALL OLLAMA: installs Ollama and the selected local model.
3. INSTALL HANDY: installs Python if needed, speech dependencies, Piper voice, wake model and Windows Terminal; creates a desktop shortcut.
4. CONFIGURE AUDIO: choose and test microphone, speakers or headphones. Select the same microphone in Handy.
5. HANDY SETTINGS: configure its F2 shortcut and local post-processing provider once (see SETUP.md).
6. LAUNCH LEVI: Ollama, Piper and Levi in three tabs of one terminal window.

Settings are saved in config.local.json beside the launcher. Restart Levi after changes. Moving the package after installation requires rerunning Setup Apps to repair the virtual environment/desktop shortcut; install at its final path.

## Voice commands
- Hey Levi / Hello Levi / Levi; wait for the short ready tone, then speak. Pause 0.8 seconds to submit (editable).
- Open Chrome / open WhatsApp / open Android Studio / open VLC: desktop shortcuts are discovered on the receiving PC. Use Refresh Desktop Apps after installing an app.
- Open my workspace: runs a routine you have saved on that PC; your personal routine is not bundled.
- Tell me a story and save it / make a list and save it: generates content and writes a new file.
- Save file / save this: saves a recent answer. Files default to Documents/LeviFiles and never overwrite existing files.
- Remember this / remember that I prefer ... / save this to the database: explicit long-term memory.
- Ask the cloud ... / use the API ... / search online for ...: explicit cloud requests. Local admissions of uncertainty can also use the API backup.
- Go to sleep: closes assistant services. F8 / terminal stop: stops speech. F2 remains Handy's manual recording alternative.
- A final question can open one follow-up recording per wake; automatic listening does not repeat indefinitely.

## Terminal commands
wake on/off/status | vision on/off | actions on/off | cloud on/off/status | routines show | stop | sleep | memory status/show
Memory deletion: memory forget NUMBER; memory clear history confirm; memory clear all confirm.

## API settings
Gemini: provider `gemini`, full generateContent endpoint with `{model}`, your model IDs and key. Supports Google Search requests. Quota limits remain provider-controlled.
Other providers, including an OpenAI-compatible xAI endpoint: provider `openai-compatible`, full HTTPS chat/completions URL, exact model ID and key. These support ordinary answers/backup; web-search tools are NOT implemented for this provider in this build. Do not interpret an ordinary answer as a live search. Groq and Grok/xAI are different services.
Only explicit cloud requests and fallback send conversation text to the configured service. Keys are stored as plaintext in the private local settings file; do not upload it.

## Limits and troubleshooting
This is a Windows launcher, not unrestricted computer control. App launch success is not guaranteed by a speech acknowledgement. Wake recognition and the small local model can make errors. API 429 means quota/rate limiting, not a missing local installation. Optional vision needs its separate model download and may be slow on CPU.
No personal API keys, history, Spotify tokens or desktop paths are included. See SETUP.md and THIRD_PARTY.md. Unsigned EXEs may be blocked by Windows policy; the CMD/PowerShell entry points are also included. No security settings are changed by setup.

## Live On/Off controls
Open LIVE ON / OFF CONTROLS in the setup window while Levi is running. Toggle wake, voice replies, actions, vision and API backup immediately, stop speech, or shut down Levi. Launch Levi turns the assistant back on. Live toggles last for this session; Settings controls startup defaults. Vision still requires an installed vision model.
