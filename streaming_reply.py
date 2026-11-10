"""Stream Ollama text into ordered sentence speech while retaining the final reply."""
import json
import queue
import re
import threading
import urllib.request
from speech_text import asks_question


def stream_reply(url, payload, cancelled, speak, followup, timeout=120):
    pending = queue.Queue()
    parts = []
    buffer = ""
    spoken_count = 0
    succeeded = threading.Event()

    def playback():
        while True:
            text = pending.get()
            if text is None:
                break
            if not cancelled.is_set():
                speak(text, cancelled, allow_followup=False)
        if succeeded.is_set() and not cancelled.is_set() and asks_question("".join(parts)):
            followup(cancelled)

    threading.Thread(target=playback, name="LeviStreamingSpeech", daemon=True).start()
    request_payload = dict(payload, stream=True)
    # Action requests have already been handled by the bridge's action router.
    request_payload.pop("tools", None)
    req = urllib.request.Request(url, data=json.dumps(request_payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            for line in response:
                if not line.strip():
                    continue
                event = json.loads(line)
                if event.get("error"):
                    raise RuntimeError(event["error"])
                delta = event.get("message", {}).get("content", "")
                parts.append(delta)
                buffer += delta
                # Keep code blocks out of speech, including incomplete streamed fences.
                while buffer:
                    if buffer.lstrip().startswith("```"):
                        start = buffer.index("```")
                        end = buffer.find("```", start + 3)
                        if end < 0:
                            break
                        buffer = "Code omitted. " + buffer[end + 3:]
                    match = re.search(r"[.!?][\"']?\s+|\n", buffer)
                    cut = match.end() if match else 0
                    fence = buffer.find("```")
                    if fence >= 0 and (not cut or fence < cut):
                        cut = fence
                    if not cut and len(buffer) >= 180 and fence < 0:
                        cut = buffer.rfind(" ", 0, 180)
                    if cut <= 0:
                        break
                    chunk, buffer = buffer[:cut], buffer[cut:]
                    if chunk.strip() and spoken_count < 1600:
                        pending.put(chunk[:1600-spoken_count])
                        spoken_count += len(chunk)
            if buffer.strip() and spoken_count < 1600 and "```" not in buffer:
                pending.put(buffer[:1600-spoken_count])
        succeeded.set()
        return {"message": {"content": "".join(parts)}}
    except Exception:
        cancelled.set()
        raise
    finally:
        pending.put(None)
