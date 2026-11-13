# Fresh-PC installation

1. Extract the ZIP to a permanent writable path, such as C:/Users/YourName/Apps/LEVI-Light. Keep all files together. Do not run from inside the ZIP.
2. Open LEVI Setup.exe (or Open_Setup.cmd). Windows 10/11 x64, internet and Microsoft App Installer/winget are needed. Administrator approval may be requested by app installers.
3. Use Settings to select the local model. Default qwen3:0.6b is CPU-only. Install Ollama/models, then Install Handy/apps. Wait for each step to complete. Setup uses official package/download services and can be rerun.
4. Configure Audio: test the microphone and output. Bluetooth must be connected before choosing devices. Windows microphone privacy permission must allow desktop applications.
5. In Handy: download a small transcription model, choose the same microphone, assign F2 to Transcribe with Post-Processing. Configure a Custom/OpenAI-compatible provider with base URL http://127.0.0.1:8765/v1, model qwen3:0.6b (or your chosen model), and key local if required. Create/select a post-process prompt containing `Spoken question:` followed by Handy's transcript insertion placeholder. Use Handy's own insertion control, not a guessed placeholder. These Handy settings require one-time manual configuration.
6. Launch Levi from setup or the new desktop shortcut. Wait for Ready/listening. Say Hey Levi, wait for the tone, then speak. F2 works without the wake phrase.

## Changing configuration
Open LEVI Settings.exe or the Settings button. Audio selection/testing is in Configure Audio. Save, then restart Levi. A changed model must be downloaded through Install Ollama/models. The full API URL and API model ID must match your provider; never put the key into the URL. For OpenAI-compatible APIs use the full /v1/chat/completions endpoint. Gemini web search is supported; other provider search requires additional integration. Set API key blank to disable cloud availability.

## Saving documents
Files go to Documents/LeviFiles by default; Settings lets you choose another folder. Example: Tell me a short story and save it. Then check the folder shown in the terminal. Save file saves a recent answer; remember this saves memory instead. The small model may decline a question or generate poor content; file handling cannot make it factually accurate.

## Workspace and apps
Refresh Desktop Apps indexes only this PC's desktop .lnk shortcuts. No source PC paths are bundled. Define your own workspace by voice, for example: When I say open workspace, open Chrome and Spotify. Use routines show to verify it before relying on it. Only applications installed on that PC can open.

## Spotify
Enter your own Spotify developer client ID in Settings, configure redirect http://127.0.0.1:8888/callback in Spotify, then Connect Spotify. Playback depends on Spotify account/API eligibility and an active player. Tokens stay local and Windows-encrypted.

## Optional vision
Off by default for the CPU profile. Download the configured VISION_MODEL separately with Ollama before enabling vision. Expect higher memory use and slower responses. It is not part of the default model download.

## Distribution
Publish the files from the clean package, never your installed config.local.json, desktop_apps.json, data, .venv, voices or wake_models. .gitignore excludes these. Rebuild launchers with Build.ps1 using the Windows .NET Framework C# compiler. This package has been statically checked and compiled, not end-to-end installed on a clean Intel laptop.
