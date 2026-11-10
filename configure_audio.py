import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sounddevice as sd
root=tk.Tk(); root.title('LEVI Audio Configuration'); root.geometry('660x320')
path=Path(__file__).with_name('config.local.json')
try: config=json.loads(path.read_text()) if path.exists() else {}
except Exception as e:
    messagebox.showerror('Invalid configuration',str(e)); raise SystemExit(1)
devices=sd.query_devices(); selectors={}
for key,label,direction in [('HANDY_MICROPHONE','Microphone','input'),('HANDY_SPEAKER','Speakers / headphones','output')]:
    ttk.Label(root,text=label).pack(pady=8)
    choices=sorted(set(d['name'] for d in devices if d['max_'+direction+'_channels']))
    box=ttk.Combobox(root,values=['Windows default']+choices,width=85,state='readonly')
    box.set(config.get(key) or 'Windows default'); box.pack(); selectors[key]=box
status=tk.StringVar(value='Select the same microphone in Handy. Restart Levi after saving.')
ttk.Label(root,textvariable=status,wraplength=630).pack(pady=15)
def index(key,direction):
    name=selectors[key].get()
    if name=='Windows default': return None
    return next(i for i,d in enumerate(devices) if d['name']==name and d['max_'+direction+'_channels'])
def tone():
    try:
        dev=index('HANDY_SPEAKER','output'); rate=int(sd.query_devices(dev,'output')['default_samplerate'])
        sd.play((.08*np.sin(2*np.pi*660*np.arange(int(rate*.4))/rate)).astype('float32'),rate,device=dev)
    except Exception as e: messagebox.showerror('Audio check',str(e))
stream=None
level=0.0
def stop():
    global stream
    if stream is not None: stream.stop(); stream.close(); stream=None
def microphone():
    global stream
    stop()
    try:
        def callback(data,frames,timing,flags):
            global level
            level=float(np.sqrt(np.mean(data*data)))
        stream=sd.InputStream(device=index('HANDY_MICROPHONE','input'),channels=1,callback=callback)
        stream.start(); root.after(5000,stop)
    except Exception as e: messagebox.showerror('Microphone check',str(e))
def meter():
    if stream is not None: status.set('Speak now: microphone level '+str(round(level*100,2))+'% (5-second check)')
    root.after(100,meter)
def save():
    try:
        for key,box in selectors.items(): config[key]='' if box.get()=='Windows default' else box.get()
        temp=path.with_suffix('.tmp'); temp.write_text(json.dumps(config,indent=2)); temp.replace(path)
        status.set('Saved. Restart Levi. Select this microphone in Handy too. Wake beep uses Windows default output.')
    except Exception as e: messagebox.showerror('Save failed',str(e))
bar=ttk.Frame(root); bar.pack()
for label,cmd in [('Check microphone',microphone),('Play test tone',tone),('Save',save)]: ttk.Button(bar,text=label,command=cmd).pack(side='left',padx=8)
root.protocol('WM_DELETE_WINDOW',lambda:(stop(),sd.stop(),root.destroy()))
meter(); root.mainloop()
