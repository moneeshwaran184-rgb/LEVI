"""Low-latency, pipelined Piper speech for Levi.

Piper's HTTP endpoint returns one complete WAV per request. To start speaking
sooner, answers are split into short speakable chunks. One worker synthesizes
the chunks in order while a second worker plays them through a single
continuous sounddevice output stream. Synthesis of the next chunk overlaps
playback of the current one, and speech starts as soon as the first short
chunk is ready instead of waiting for the whole answer.
"""
from __future__ import annotations

import io
import json
import os
import queue
import re
import sys
import tempfile
import threading
import time
import urllib.request
import wave

from speech_text import clean_speech

MAX_SPEECH_CHARS = 1600
FIRST_CHUNK_CHARS = 140
NEXT_CHUNK_CHARS = 280
SENTENCE_PAUSE_SECONDS = 0.12
CLAUSE_PAUSE_SECONDS = 0.04
WRITE_BLOCK_SECONDS = 0.05

_SENTENCE_END = re.compile(r"[.!?][\"'\u201d\u2019)\]]*\s+")
_CLAUSE_END = re.compile(r"[,;:]\s+")


def _cut_position(text: str, limit: int) -> int:
    """Return the best cut point in text, or 0 when more text is needed."""
    if not text:
        return 0
    match = _SENTENCE_END.search(text)
    if match and match.end() <= limit:
        return match.end()
    if len(text) <= limit:
        return 0
    # If a sentence ends just after the soft limit, wait for it so the voice
    # keeps a natural sentence boundary.
    if match and match.end() <= int(limit * 1.5):
        return match.end()
    newline = text.find("\n")
    if 0 <= newline < limit:
        return newline + 1
    head = text[:limit]
    clause = 0
    for clause_match in _CLAUSE_END.finditer(head):
        if clause_match.end() >= max(40, limit // 2):
            clause = clause_match.end()
    if clause:
        return clause
    space = head.rfind(" ")
    return space + 1 if space >= 40 else limit


class SpeechChunker:
    """Turn a streamed answer into short, ordered speakable chunks."""

    def __init__(self, first_limit: int = FIRST_CHUNK_CHARS,
                 limit: int = NEXT_CHUNK_CHARS,
                 max_chars: int = MAX_SPEECH_CHARS):
        self._buffer = ""
        self._first = True
        self._in_fence = False
        self._first_limit = max(40, int(first_limit))
        self._limit = max(self._first_limit, int(limit))
        self._remaining = max(0, int(max_chars))

    def feed(self, text: str) -> list[str]:
        if text:
            self._buffer += text
        chunks: list[str] = []
        while self._remaining > 0:
            chunk = self._take()
            if not chunk:
                break
            chunks.append(chunk)
            self._remaining -= len(chunk)
        if self._remaining <= 0:
            self._buffer = ""
        return chunks

    def flush(self) -> list[str]:
        chunks: list[str] = []
        if self._remaining <= 0:
            self._buffer = ""
            return chunks
        text = self._buffer.strip()
        self._buffer = ""
        self._in_fence = False
        if "```" in text:
            text = text.split("```", 1)[0].strip()
        if text:
            text = text[: self._remaining]
            chunks.append(text)
            self._remaining -= len(text)
        return chunks

    def _take(self) -> str | None:
        while True:
            buffer = self._buffer.lstrip()
            self._buffer = buffer
            if not buffer:
                return None
            if self._in_fence:
                end = buffer.find("```")
                if end < 0:
                    self._buffer = ""
                    return None
                self._buffer = buffer[end + 3:]
                self._in_fence = False
                continue
            start = buffer.find("```")
            if start >= 0:
                end = buffer.find("```", start + 3)
                if end < 0:
                    before = buffer[:start]
                    self._buffer = ""
                    self._in_fence = True
                    return self._emit(before)
                self._buffer = buffer[:start] + " Code omitted. " + buffer[end + 3:]
                continue
            limit = self._first_limit if self._first else self._limit
            cut = _cut_position(buffer, limit)
            if cut <= 0:
                return None
            chunk = buffer[:cut]
            self._buffer = buffer[cut:]
            return self._emit(chunk)

    def _emit(self, text: str) -> str | None:
        text = text.strip()
        if not text:
            return None
        self._first = False
        return text


class SpeechPlayer:
    """Synthesize and play chunks in parallel with a bounded prefetch queue."""

    def __init__(self, piper_url: str, cancelled: threading.Event,
                 playback_lock: threading.Lock | None = None,
                 speaker: str = "", logger=print):
        self.piper_url = piper_url.rstrip("/")
        self.cancelled = cancelled
        self.playback_lock = playback_lock or threading.Lock()
        self.speaker = speaker or ""
        self.logger = logger
        self._text: queue.Queue[str] = queue.Queue(maxsize=6)
        self._audio: queue.Queue[tuple[bytes, float] | None] = queue.Queue(maxsize=3)
        self._closed = False
        self._failed = False
        self._stopped = threading.Event()
        self._playback_started = threading.Event()
        self._synth_done = threading.Event()
        self._play_done = threading.Event()
        self._synth_thread = threading.Thread(
            target=self._synthesize, name="LeviSynth", daemon=True)
        self._play_thread = threading.Thread(
            target=self._playback, name="LeviPlayback", daemon=True)
        self._synth_thread.start()
        self._play_thread.start()

    def feed(self, text: str) -> None:
        if self._closed or not text:
            return
        text = clean_speech(text)
        if not text:
            return
        while not self._halted():
            try:
                self._text.put(text, timeout=0.2)
                return
            except queue.Full:
                continue

    def finish(self) -> None:
        self._closed = True

    def stop(self) -> None:
        """Silence this reply only; the question itself stays active."""
        self._stopped.set()
        if sys.platform == "win32":
            try:
                import winsound

                winsound.PlaySound(None, 0)
            except Exception:
                pass

    def cancel(self) -> None:
        self.cancelled.set()
        self.stop()
        self.finish()

    def _halted(self) -> bool:
        return self.cancelled.is_set() or self._stopped.is_set()

    def wait(self, timeout: float | None = None) -> None:
        self.finish()
        self._play_done.wait(timeout)
        self._synth_done.wait(timeout)

    @property
    def done(self) -> bool:
        return self._play_done.is_set()

    def _synthesize(self) -> None:
        try:
            # Wait until playback owns the shared lock so a new answer does not
            # synthesize far ahead of the answer that is still being spoken.
            self._playback_started.wait(timeout=5.0)
            while not self._halted():
                try:
                    text = self._text.get(timeout=0.2)
                except queue.Empty:
                    if self._closed:
                        break
                    continue
                if self._halted():
                    break
                wav = self._request_wav(text)
                if wav is None:
                    if self._failed:
                        break
                    continue
                pause = (SENTENCE_PAUSE_SECONDS
                         if text.rstrip().endswith((".", "!", "?"))
                         else CLAUSE_PAUSE_SECONDS)
                while not self._halted():
                    try:
                        self._audio.put((wav, pause), timeout=0.2)
                        break
                    except queue.Full:
                        continue
        finally:
            while True:
                try:
                    self._audio.put(None, timeout=0.2)
                    break
                except queue.Full:
                    try:
                        self._audio.get_nowait()
                    except queue.Empty:
                        pass
            self._synth_done.set()

    def _request_wav(self, text: str) -> bytes | None:
        if self._halted() or self._failed:
            return None
        try:
            request = urllib.request.Request(
                self.piper_url + "/synthesize",
                data=json.dumps({"text": text}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                wav = response.read()
        except Exception as exc:
            self._failed = True
            if not self._halted():
                self.logger(f"[Piper warning] Could not synthesize speech: {exc}", flush=True)
            return None
        if not wav.startswith(b"RIFF"):
            self._failed = True
            if not self._halted():
                self.logger("[Piper warning] Piper did not return a WAV file.", flush=True)
            return None
        return wav

    def _playback(self) -> None:
        try:
            with self.playback_lock:
                self._playback_started.set()
                if self._halted():
                    return
                try:
                    self._play_streaming()
                except Exception as exc:
                    if not self._halted():
                        self.logger(
                            f"[Piper warning] Streaming playback unavailable ({exc}); "
                            "using the fallback player.", flush=True)
                    self._play_fallback()
        finally:
            self._playback_started.set()
            self._drain_audio()
            self._play_done.set()

    def _next_audio(self) -> tuple[bytes, float] | None:
        while not self._halted():
            try:
                item = self._audio.get(timeout=0.2)
            except queue.Empty:
                if self._synth_done.is_set():
                    return None
                continue
            return item
        return None

    def _play_streaming(self) -> None:
        import sounddevice as sd

        stream = None
        rate = 0
        channels = 0
        try:
            while not self._halted():
                item = self._next_audio()
                if item is None:
                    break
                wav, pause = item
                frames, sample_rate, sample_channels, _ = _decode_wav(wav)
                if stream is None:
                    rate, channels = sample_rate, sample_channels
                    stream = _open_output_stream(sd, rate, channels, self.speaker)
                if (sample_rate, sample_channels) != (rate, channels):
                    continue
                block = max(256, int(rate * WRITE_BLOCK_SECONDS)) * channels
                for start in range(0, len(frames), block):
                    if self._halted():
                        break
                    stream.write(frames[start:start + block])
                if self._halted():
                    break
                _write_silence(stream, rate, channels, pause)
        finally:
            if stream is not None:
                try:
                    stream.stop()
                except Exception:
                    pass
                try:
                    stream.close()
                except Exception:
                    pass

    def _play_fallback(self) -> None:
        if sys.platform != "win32":
            self.logger("Piper audio generated; automatic playback is Windows-only.", flush=True)
            self._drain_audio()
            return
        import winsound

        while not self._halted():
            item = self._next_audio()
            if item is None:
                break
            wav, pause = item
            fd, wav_path = tempfile.mkstemp(prefix="levi_reply_", suffix=".wav")
            try:
                with os.fdopen(fd, "wb") as audio_file:
                    audio_file.write(wav)
                with wave.open(wav_path, "rb") as audio:
                    duration = audio.getnframes() / audio.getframerate()
                winsound.PlaySound(
                    wav_path,
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
                )
                deadline = time.monotonic() + duration + pause + 0.2
                while not self._halted() and time.monotonic() < deadline:
                    time.sleep(0.05)
            finally:
                try:
                    os.unlink(wav_path)
                except OSError:
                    pass

    def _drain_audio(self) -> None:
        while True:
            try:
                self._audio.get_nowait()
            except queue.Empty:
                break


def _decode_wav(data: bytes) -> tuple[bytes, int, int, int]:
    with wave.open(io.BytesIO(data), "rb") as audio:
        if audio.getsampwidth() != 2:
            raise ValueError("Piper returned non-16-bit audio")
        return (audio.readframes(audio.getnframes()), audio.getframerate(),
                audio.getnchannels(), audio.getsampwidth())


def _open_output_stream(sd, rate: int, channels: int, speaker: str):
    device = None
    if speaker:
        device = next(
            (index for index, info in enumerate(sd.query_devices())
             if info.get("name") == speaker and info.get("max_output_channels", 0)),
            None,
        )
        if device is None:
            print("[Piper warning] Configured speaker not found; using Windows default.", flush=True)
    stream = sd.RawOutputStream(
        samplerate=rate, channels=channels, dtype="int16", device=device)
    stream.start()
    return stream


def _write_silence(stream, rate: int, channels: int, seconds: float) -> None:
    frames = int(rate * max(0.0, seconds))
    if frames > 0:
        stream.write(b"\x00\x00" * (frames * channels))


def stream_reply(url: str, payload: dict, cancelled: threading.Event,
                 player: SpeechPlayer, timeout: float = 120, gate=None):
    """Stream Ollama tokens into a SpeechPlayer and return the full reply.

    ``gate`` is called once with the first speakable chunk. Returning False keeps
    the text for the caller but suppresses playback (for example, when the local
    model admits it does not know the answer and a cloud fallback will speak).
    """
    chunker = SpeechChunker()
    parts: list[str] = []
    speaking = True
    gated = False
    request_payload = dict(payload, stream=True)
    # The bridge's action router has already handled any tool calls.
    request_payload.pop("tools", None)
    request = urllib.request.Request(
        url, data=json.dumps(request_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for line in response:
                if not line.strip():
                    continue
                event = json.loads(line)
                if event.get("error"):
                    raise RuntimeError(event["error"])
                delta = event.get("message", {}).get("content", "")
                if not delta:
                    continue
                parts.append(delta)
                if not cancelled.is_set():
                    for chunk in chunker.feed(delta):
                        if gate is not None and not gated:
                            gated = True
                            speaking = bool(gate(chunk))
                        if speaking:
                            player.feed(chunk)
        if not cancelled.is_set():
            for chunk in chunker.flush():
                if gate is not None and not gated:
                    gated = True
                    speaking = bool(gate(chunk))
                if speaking:
                    player.feed(chunk)
        return {"message": {"content": "".join(parts)}}
    except Exception:
        cancelled.set()
        player.cancel()
        raise
    finally:
        player.finish()
