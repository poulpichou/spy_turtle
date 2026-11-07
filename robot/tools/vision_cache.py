"""Cache OpenCV face embeddings; model and reference photo changes invalidate the cache."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'cache'/'vision'/'faces.npz'
def load_or_build(detector,recognizer,models,faces_dir):
 import cv2,numpy as np
 files=[p for folder in sorted(faces_dir.iterdir()) if folder.is_dir() for p in sorted(folder.iterdir()) if p.suffix.lower() in ('.jpg','.jpeg','.png','.webp')] if faces_dir.is_dir() else []
 models=[Path(p) for p in models]
 signature=[(str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in [*models,*files]]
 digest=hashlib.sha256(json.dumps([1,signature],ensure_ascii=False).encode()).hexdigest()
 try:
  with np.load(CACHE,allow_pickle=False) as data:
   if str(data['key'])==digest:
    names=[str(n) for n in data['names']];features=data['features']
    if len(names)==len(features):return list(zip(names,[features[i] for i in range(len(names))])),0,True
 except (OSError,ValueError,KeyError,EOFError):pass
 refs=[];skipped=0
 for path in files:
  img=cv2.imread(str(path))
  if img is None:skipped+=1;continue
  detector.setInputSize((img.shape[1],img.shape[0]));_,found=detector.detect(img)
  if found is None or len(found)!=1:skipped+=1;continue
  try:refs.append((path.parent.name,recognizer.feature(recognizer.alignCrop(img,found[0]))))
  except Exception:skipped+=1
 CACHE.parent.mkdir(parents=True,exist_ok=True);tmp=CACHE.with_suffix('.part')
 try:
  with tmp.open('wb') as out:np.savez_compressed(out,key=np.array(digest),names=np.array([name for name,_ in refs],dtype=str),features=np.stack([feat for _,feat in refs]) if refs else np.empty((0,128),dtype=np.float32))
  tmp.replace(CACHE)
 finally:tmp.unlink(missing_ok=True)
 return refs,skipped,False
