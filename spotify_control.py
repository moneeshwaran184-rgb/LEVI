import base64, ctypes, hashlib, json, os, re, secrets, threading, time, urllib.parse, urllib.request, urllib.error, webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
REDIRECT = 'http://127.0.0.1:8888/callback'
TOKEN = Path(__file__).parent / 'data' / 'spotify-token.dpapi'
LOCK = threading.RLock()
class Blob(ctypes.Structure):
    _fields_ = [('size', ctypes.c_ulong), ('data', ctypes.POINTER(ctypes.c_ubyte))]
def protect(data, decrypt=False):
    buffer = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    target = Blob()
    lib = ctypes.windll.crypt32
    fn = lib.CryptUnprotectData if decrypt else lib.CryptProtectData
    if not fn(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise RuntimeError('Windows could not access Spotify credentials.')
    try: return ctypes.string_at(target.data, target.size)
    finally: ctypes.windll.kernel32.LocalFree(target.data)
def save(tokens):
    tokens['expires_at'] = time.time() + tokens.get('expires_in',3600)
    TOKEN.parent.mkdir(exist_ok=True)
    temp = TOKEN.with_suffix('.tmp')
    temp.write_bytes(protect(json.dumps(tokens).encode()))
    temp.replace(TOKEN)
def token_request(fields):
    request = urllib.request.Request('https://accounts.spotify.com/api/token', data=urllib.parse.urlencode(fields).encode())
    with urllib.request.urlopen(request,timeout=20) as response: return json.load(response)
def access_token(force=False):
    with LOCK:
        if not TOKEN.exists(): raise RuntimeError('Spotify needs authorization. Run Connect_Spotify.cmd first.')
        tokens=json.loads(protect(TOKEN.read_bytes(),True))
        if force or time.time() >= tokens['expires_at']-60:
            fresh=token_request({'grant_type':'refresh_token','refresh_token':tokens['refresh_token'],'client_id':CLIENT_ID})
            fresh.setdefault('refresh_token',tokens['refresh_token']); save(fresh); tokens=fresh
        return tokens['access_token']
def api(path, method='GET', body=None, retry=True):
    request=urllib.request.Request('https://api.spotify.com/v1'+path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':'Bearer '+access_token(),'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=20) as response:
            raw=response.read();return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        if exc.code==401 and retry:
            access_token(True);return api(path,method,body,False)
        messages={403:'Spotify refused playback. Check Premium and add your account under the developer app user access settings.',404:'Open Spotify on your PC and play something once so it becomes available.',429:'Spotify is limiting requests. Please try again later.'}
        raise RuntimeError(messages.get(exc.code, f'Spotify returned error {exc.code}.')) from None
def device_id():
    devices=[d for d in api('/me/player/devices').get('devices',[]) if not d.get('is_restricted')]
    computers=[d for d in devices if d.get('type')=='Computer']
    local=[d for d in computers if d.get('name','').casefold()==os.environ.get('COMPUTERNAME','').casefold()]
    choices=local or [d for d in computers if d.get('is_active')] or (computers if len(computers)==1 else [])
    if not choices: raise RuntimeError('Open Spotify on this computer and play something once. I could not identify the desktop player.')
    return choices[0]['id']
def control(question):
    try:
        text=question.strip().lower();device=urllib.parse.quote(device_id(),safe='');suffix='?device_id='+device
        if re.search(r'\b(pause|stop)\b',text): api('/me/player/pause'+suffix,'PUT'); return 'Paused Spotify.'
        if re.search(r'\b(next|skip)\b',text): api('/me/player/next'+suffix,'POST');return 'Skipped to the next track.'
        if re.search(r'\b(previous|back)\b',text): api('/me/player/previous'+suffix,'POST');return 'Playing the previous track.'
        query=re.sub(r'^.*?\b(?:play|resume)\s*','',text)
        query=re.sub(r'\s+(?:on|in|using)\s+spotify.*$','',query).strip(' .!?')
        if query in ('','spotify','music','songs','some music','some songs','a song'):
            api('/me/player/play'+suffix,'PUT');return 'Resumed Spotify.'
        query=re.sub(r'^(?:the song|the track|song|track)\s+','',query)
        parts=re.split(r'\s+by\s+',query,maxsplit=1)
        search=f'track:{parts[0]} artist:{parts[1]}' if len(parts)==2 else query
        tracks=api('/search?'+urllib.parse.urlencode({'q':search,'type':'track','limit':5})).get('tracks',{}).get('items',[])
        tracks=[t for t in tracks if t and t.get('is_playable',True)]
        if not tracks:return 'I could not find that song on Spotify. Try the song title and artist.'
        track=tracks[0];api('/me/player/play'+suffix,'PUT',{'uris':[track['uri']]})
        return 'Playing '+track['name']+' by '+', '.join(a['name'] for a in track['artists'])+'.'
    except Exception as exc:return 'Spotify: '+str(exc)
def connect():
    verifier=secrets.token_urlsafe(64);state=secrets.token_urlsafe(32)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    result={}
    class Callback(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            parsed=urllib.parse.urlsplit(self.path);params=urllib.parse.parse_qs(parsed.query)
            if parsed.path!='/callback' or not secrets.compare_digest(params.get('state',[''])[0],state):
                self.send_error(400,'Invalid authorization callback');return
            try:
                if 'error' in params:raise RuntimeError('Spotify authorization was declined.')
                tokens=token_request({'grant_type':'authorization_code','code':params['code'][0],'redirect_uri':REDIRECT,'client_id':CLIENT_ID,'code_verifier':verifier})
                save(tokens);result['ok']=True;message='Spotify connected to Levi. You can close this tab.'
            except Exception:
                result['error']=True;message='Spotify connection failed. Run Connect_Spotify.cmd to retry.'
            self.send_response(200);self.send_header('Content-Type','text/plain');self.end_headers();self.wfile.write(message.encode())
    with HTTPServer(('127.0.0.1',8888),Callback) as server:
        server.timeout=1
        url='https://accounts.spotify.com/authorize?'+urllib.parse.urlencode({'client_id':CLIENT_ID,'response_type':'code','redirect_uri':REDIRECT,'scope':'user-read-playback-state user-modify-playback-state','code_challenge_method':'S256','code_challenge':challenge,'state':state})
        webbrowser.open(url);print('Approve playback access in the Spotify browser page. Waiting up to 10 minutes.',flush=True)
        deadline=time.time()+600
        while not result and time.time()<deadline:server.handle_request()
    print('Spotify connected.' if result.get('ok') else 'Authorization not completed.',flush=True)
if __name__=='__main__':connect()
