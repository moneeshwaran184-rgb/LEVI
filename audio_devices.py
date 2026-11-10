import os, wave
import numpy as np
import sounddevice as sd
def play_wav(path):
    name = os.environ.get('HANDY_SPEAKER', '')
    device = None
    if name:
        device = next((i for i,d in enumerate(sd.query_devices()) if d['name']==name and d['max_output_channels']), None)
        if device is None: raise RuntimeError('Speaker disconnected. Open Configure Audio.exe.')
    with wave.open(path, 'rb') as w:
        if w.getsampwidth()!=2: raise ValueError('Expected 16-bit audio')
        data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).reshape(-1,w.getnchannels())
        sd.play(data,w.getframerate(),device=device,blocking=False)
