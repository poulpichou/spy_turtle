#!/usr/bin/env python3
"""Download 7 official Piper voices to models/voices (standard library only)."""
import hashlib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1] if Path(__file__).parent.name=='scripts' else Path.cwd()
DEST=ROOT/'models'/'voices'
INDEX='https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json'
BASE='https://huggingface.co/rhasspy/piper-voices/resolve/main/'
VOICES=('en_US-bryce-medium','en_US-amy-medium','en_GB-alba-medium','en_GB-northern_english_male-medium','fr_FR-gilles-low','fr_FR-tom-medium','fr_FR-upmc-medium')
def fetch(url,target,expected=None):
    if target.is_file() and target.stat().st_size and (not expected or hashlib.md5(target.read_bytes()).hexdigest()==expected):
        print('  OK (cached)',target.name,flush=True);return
    tmp=target.with_name(target.name+'.part');h=hashlib.md5()
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SpyTurtle-VoiceInstaller/1.0'}),timeout=90) as response,tmp.open('wb') as out:
            while True:
                chunk=response.read(1024*1024)
                if not chunk:break
                out.write(chunk);h.update(chunk)
        if expected and h.hexdigest()!=expected:raise RuntimeError('Checksum mismatch: '+target.name)
        if tmp.stat().st_size==0:raise RuntimeError('Empty download: '+target.name)
        tmp.replace(target);print('  downloaded',target.name,flush=True)
    except Exception:tmp.unlink(missing_ok=True);raise
def main():
    DEST.mkdir(parents=True,exist_ok=True)
    print('Fetching official Piper voice catalog...',flush=True)
    with urllib.request.urlopen(INDEX,timeout=90) as response:catalog=json.load(response)
    for voice in VOICES:
        print('Voice:',voice,flush=True)
        if voice not in catalog:raise RuntimeError('Voice absent from catalog: '+voice)
        files=catalog[voice]['files']
        for remote,meta in files.items():
            filename=remote.rsplit('/',1)[-1]
            if filename=='MODEL_CARD':filename=voice+'.MODEL_CARD'
            if not (filename.endswith('.onnx') or filename.endswith('.onnx.json') or filename.endswith('.MODEL_CARD')):continue
            fetch(BASE+remote+'?download=true',DEST/filename,meta.get('md5_digest'))
    print('All 7 voices installed in',DEST,flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:print('ERROR:',e,file=sys.stderr);sys.exit(1)
