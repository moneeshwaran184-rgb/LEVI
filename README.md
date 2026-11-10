# LEVI — local Windows voice assistant

LEVI combines Handy speech recognition, Ollama reasoning, Piper speech and Vosk wake detection. Windows 10/11 x64; internet required for installation and online actions. Local conversation can run offline after downloads.

## Start here

1. Download/extract this whole folder. Keep the EXEs beside the scripts.
2. Run **1-Setup-Models.exe**: installs Ollama and downloads qwen3:4b-instruct and qwen3-vl:8b-instruct.
3. Run **2-Setup-Apps.exe**: installs Python and Handy, creates a virtual environment, downloads Piper High and the Vosk wake model, and creates a Desktop LEVI shortcut.
4. Read **SETUP.md** for Handy's required first-run transcription model, microphone, F2 and post-processing settings.
5. Run **Configure Audio.exe** to choose microphone and speakers/headphones.
6. Open **LEVI.exe** or the Desktop shortcut. Ollama, Piper and LEVI appear as tabs in one Windows Terminal window.

The EXEs are small native launchers, not self-contained AI models. Models and Python dependencies install separately. Source and Build.ps1 are included for rebuilding the launchers.

## Features

- Hey Levi, Hello Levi, or Levi wake words; stronger confidence requirement for the single-word trigger.
- F2 fallback through Handy's configured shortcut. F8 or terminal stop interrupts speech.
- Custom wake MP3 in assets/wake.mp3.
- Normal conversational answers stream from Ollama into sentence-sized Piper requests; each sentence is synthesized before playback. This is not raw sample-by-sample TTS. Action/vision responses follow their normal completion path.
- Emoji/Markdown cleanup before speech; follow-up listening after detected questions, after playback finishes. Silence cancels recording after nine seconds; speech submits after about one second of silence.
- Text model stays warm for 45 seconds; vision model unloads after use.
- On-demand screen vision enabled at startup; no continuous screenshot scanning.
- Persistent SQLite conversation history, explicitly remembered facts and saved app routines.
- Approved desktop apps, websites, browser searches and optional Spotify playback controls.
- Wake, actions and memory enabled by default. Vision can be disabled in the terminal.
- Local audio selectors, test tone and microphone level check. Wake MP3 uses Windows default output; select that output in Windows Sound settings if needed.

## Voice examples

- “Hey Levi” / “Hello Levi” / “Levi”, then speak after the wake sound.
- “Remember that I prefer the desktop app.”
- “Remember this” or “save into the database”: saves the preceding stored user statement.
- “Save into the database that I like jazz.”
- “What do you remember about me?”
- “Open Spotify”, “open WhatsApp”, “search for Python tutorials”.
- “Play [song] on Spotify”, “pause Spotify”, “next on Spotify” (requires Spotify setup).
- “What is on my screen?”
- “When I say workspace, open Chrome and Spotify.” Then “open workspace”.

## Bridge terminal commands

| Command | Effect |
|---|---|
| wake on / off / status | Control wake microphone |
| vision on / off / status / show | Control and inspect on-demand vision |
| actions on / off / status | Enable or disable computer actions |
| routines show | List saved routines |
| stop | Stop current speech |
| memory status / show | Inspect saved memory |
| memory forget NUMBER | Delete a listed remembered fact |
| memory clear history | Show confirmation command to erase history |
| memory clear all | Show confirmation command to erase history and facts |
| Ctrl+C | Stop the service in the selected terminal tab |

Memory resides in data/assistant_memory.sqlite3. Spotify tokens are encrypted with Windows DPAPI in data/. No personal memory or credentials ship with this repository. Screenshots and microphone recordings are not stored in the memory database. Stored facts are short notes (currently capped at 240 characters), and only a bounded selection enters each model request.

## Limitations and status

Piper does not provide explicit emotional acting controls. Wake accuracy depends on room noise and microphone choice. Follow-up detection uses text heuristics. F2 must be assigned in Handy. Bluetooth microphone mode can change headset sound quality. Only one Levi bridge can use the default ports at a time. Hardware latency and clean-machine installation have not been certified; syntax/build checks do not prove headset or voice behavior.

## GitHub distribution

Commit source, docs, setup scripts and launcher EXEs. .gitignore excludes models, environments, local config, logs, tokens and memory. Do not add personal data with git add -f. Nothing here uploads to GitHub automatically. Large models are downloaded during setup. The included custom sound was supplied by the project owner; confirm redistribution rights before publishing it. Third-party applications and models keep their respective licenses; see THIRD_PARTY.md.
