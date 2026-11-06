import json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from robot.speech import tts,cache
from robot.config import settings

def main():
 config=json.loads((ROOT/'robot/config/sentinel.json').read_text(encoding='utf-8'))
 people=sorted(p.name.replace('_',' ') for p in (ROOT/'robot/assets/faces').iterdir() if p.is_dir()) if (ROOT/'robot/assets/faces').is_dir() else []
 if not people:print('No known faces in robot/assets/faces; nothing to pre-generate');return
 done=skipped=0
 for lang in tts.LANGUAGES:
  model=tts.voice_path(lang)
  if not model.is_file():print('Missing model:',model);continue
  for person in people:
   for phrase in config['phrases'].get(lang,[]):
    text=phrase.format(name=person)
    effects=tts.tuning();identifier=cache.key(text,lang,model,effects)
    if cache.valid(cache.FOLDER/(identifier+'.wav')):skipped+=1;continue
    with tempfile.TemporaryDirectory(prefix='spy_cache_') as folder:
     target=Path(folder)/'voice.wav'
     command=[sys.executable,'-m','piper','-m',str(model),'-f',str(target),'--',text]
     result=subprocess.run(command,capture_output=True,text=True,timeout=settings.TTS_TIMEOUT)
     if result.returncode:print('ERROR',lang,person,result.stderr[-300:]);continue
     tts.process_audio(target,effects['pitch'],effects['speed']);cache.store(identifier,target);done+=1
     print(f'Cached {lang} / {person}: {text}')
 print(f'Done: {done} generated, {skipped} already cached')
if __name__=='__main__':main()
