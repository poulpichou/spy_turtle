import os
import time
from collections import deque
from io import BytesIO
from pathlib import Path
from threading import Lock, Thread

from robot.utils.logger import log

ROOT=Path(__file__).resolve().parents[1]/'assets'

class FaceVision:
    def __init__(self):
        self.lock=Lock();self.enabled=False;self.interval=2;self.busy=False;self.last_start=0
        self.faces=[];self.stats=deque(maxlen=100);self.errors=0;self.last_error=None
        self.detector=None;self.recognizer=None;self.references=[]
    def status(self):
        with self.lock:
            durations=list(self.stats)
            return {'enabled':self.enabled,'interval':self.interval,'faces':list(self.faces),'busy':self.busy,'references':len(self.references),'errors':self.errors,'last_error':self.last_error,'last_ms':round(durations[-1],1) if durations else None,'avg_ms':round(sum(durations)/len(durations),1) if durations else None,'max_ms':round(max(durations),1) if durations else None}
    def enable(self,enabled):
        if not enabled:
            with self.lock:self.enabled=False;self.faces=[]
            log.info('[FACE] recognition disabled');return self.status()
        with self.lock:
            if self.enabled:return self.status_unlocked()
        self._load()
        with self.lock:self.enabled=True
        log.info(f'[FACE] recognition enabled interval={self.interval}s references={len(self.references)}')
        return self.status()
    def status_unlocked(self):return {'enabled':self.enabled,'interval':self.interval,'faces':list(self.faces),'busy':self.busy,'references':len(self.references),'errors':self.errors,'last_error':self.last_error}
    def configure(self,interval):
        if interval not in (1,2,3,4,5):raise ValueError('Interval must be 1..5 seconds')
        with self.lock:self.interval=interval
        log.info(f'[FACE] interval set to {interval}s')
        return self.status()
    def _load(self):
        import cv2
        t=time.perf_counter();models=ROOT/'models'
        detector=cv2.FaceDetectorYN.create(str(models/'face_detection_yunet_2023mar.onnx'),'',(320,320))
        recognizer=cv2.FaceRecognizerSF.create(str(models/'face_recognition_sface_2021dec.onnx'),'')
        refs=[];skipped=0
        for folder in sorted((ROOT/'faces').iterdir()) if (ROOT/'faces').exists() else []:
            if not folder.is_dir():continue
            for path in sorted(folder.iterdir()):
                if path.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):continue
                img=cv2.imread(str(path))
                if img is None:skipped+=1;log.warn(f'[FACE] cannot read reference: {folder.name}/{path.name}');continue
                detector.setInputSize((img.shape[1],img.shape[0]))
                _,faces=detector.detect(img)
                if faces is None or len(faces)!=1:skipped+=1;log.warn(f'[FACE] reference needs exactly one face: {folder.name}/{path.name}');continue
                try:refs.append((folder.name,recognizer.feature(recognizer.alignCrop(img,faces[0]))))
                except Exception as exc:skipped+=1;log.warn(f'[FACE] reference failed: {folder.name}/{path.name}: {exc}')
        self.detector=detector;self.recognizer=recognizer;self.references=refs
        log.info(f'[FACE] models loaded in {(time.perf_counter()-t)*1000:.0f}ms; references={len(refs)} skipped={skipped}')
    def submit(self,jpeg):
        now=time.monotonic()
        with self.lock:
            if not self.enabled or self.busy or now-self.last_start<self.interval:return
            self.busy=True;self.last_start=now
        Thread(target=self._process,args=(jpeg,),daemon=True,name='face-vision').start()
    def _process(self,jpeg):
        import cv2
        import numpy as np
        t=time.perf_counter()
        try:
            tc=time.perf_counter();img=cv2.imdecode(np.frombuffer(jpeg,dtype=np.uint8),cv2.IMREAD_COLOR)
            if img is None:raise ValueError('Cannot decode camera JPEG')
            capture_ms=(time.perf_counter()-tc)*1000
            td=time.perf_counter();height,width=img.shape[:2];self.detector.setInputSize((width,height));_,detected=self.detector.detect(img)
            detection_ms=(time.perf_counter()-td)*1000;tr=time.perf_counter();result=[]
            for face in [] if detected is None else detected:
                x,y,w,h=[float(v) for v in face[:4]];name='unknown';best=0.0
                feature=self.recognizer.feature(self.recognizer.alignCrop(img,face))
                for person,ref in self.references:
                    score=float(self.recognizer.match(feature,ref,cv2.FaceRecognizerSF_FR_COSINE))
                    if score>best:best=score;name=person
                if best<0.45:name='unknown'
                result.append({'x':max(0,x/width),'y':max(0,y/height),'w':min(1,w/width),'h':min(1,h/height),'name':name})
            recognition_ms=(time.perf_counter()-tr)*1000;total_ms=(time.perf_counter()-t)*1000
            with self.lock:
                if self.enabled:self.faces=result
                self.stats.append(total_ms);self.last_error=None
            log.debug(f'[FACE] decode={capture_ms:.0f}ms detect={detection_ms:.0f}ms recognition={recognition_ms:.0f}ms faces={len(result)} names={[r["name"] for r in result]}')
            log.info(f'[FACE] cycle={total_ms:.0f}ms faces={len(result)} interval={self.interval}s')
        except Exception as error:
            with self.lock:self.errors+=1;self.last_error=str(error);self.faces=[]
            log.error(f'[FACE] cycle error: {error}')
        finally:
            with self.lock:self.busy=False

vision=FaceVision()
