import hashlib,json,shutil,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'cache'/'speech'
def key(text,language,model,tuning):
 stat=model.stat()
 data={'text':text,'language':language,'model':model.name,'size':stat.st_size,'mtime_ns':stat.st_mtime_ns,'pitch':tuning['pitch'],'speed':tuning['speed'],'version':1}
 return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def valid(path):
 try:
  if not path.is_file() or path.stat().st_size<44:return False
  with wave.open(str(path),'rb') as wav:return wav.getnframes()>0
 except (OSError,EOFError,wave.Error):return False
def restore(identifier,target):
 source=FOLDER/(identifier+'.wav')
 if not valid(source):return False
 shutil.copyfile(source,target);return True
def store(identifier,source):
 FOLDER.mkdir(parents=True,exist_ok=True)
 dest=FOLDER/(identifier+'.wav');temp=FOLDER/(identifier+'.part')
 try:shutil.copyfile(source,temp);temp.replace(dest)
 finally:temp.unlink(missing_ok=True)
