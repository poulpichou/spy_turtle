import threading,time
from pathlib import Path
from robot.config import settings

ROOT=Path(__file__).resolve().parents[1]
FACES=ROOT/'assets/faces'
MODELS=ROOT/'assets/models'

class FaceVision:
    def __init__(self):
        self.lock=threading.RLock();self.enabled=False;self.pending=None;self.faces=[];self.updated_at=0.;self.error=None
        self.detector=None;self.recognizer=None;self.known=[];self.stop_event=threading.Event();self.worker=None
    def _load(self):
        import cv2
        detection=MODELS/'face_detection_yunet_2023mar.onnx'
        recognition=MODELS/'face_recognition_sface_2021dec.onnx'
        if not detection.is_file() or not recognition.is_file():raise RuntimeError('Missing face models: run python scripts/install_face_models.py')
        detector=cv2.FaceDetectorYN.create(str(detection),'',(320,320),score_threshold=0.8)
        recognizer=cv2.FaceRecognizerSF.create(str(recognition),'')
        known=[]
        for folder in sorted(FACES.iterdir()) if FACES.is_dir() else []:
            if not folder.is_dir():continue
            for path in sorted(folder.iterdir()):
                if path.suffix.lower() not in ('.jpg','.jpeg','.png'):continue
                img=cv2.imread(str(path))
                if img is None:continue
                h,w=img.shape[:2];detector.setInputSize((w,h));_,faces=detector.detect(img)
                if faces is None or len(faces)!=1:continue
                known.append((folder.name,recognizer.feature(recognizer.alignCrop(img,faces[0]))))
        return detector,recognizer,known
    def enable(self,value):
        value=bool(value)
        with self.lock:
            if value==self.enabled:return self.status()
            if value:
                try:detector,recognizer,known=self._load()
                except Exception as exc:self.error=str(exc);raise
                self.detector=detector;self.recognizer=recognizer;self.known=known
                self.faces=[];self.updated_at=0.;self.error=None;self.pending=None;self.stop_event.clear();self.enabled=True
                self.worker=threading.Thread(target=self._loop,daemon=True,name='face-vision');self.worker.start()
            else:
                self.enabled=False;self.stop_event.set();self.pending=None;self.faces=[];self.updated_at=0.
        return self.status()
    def submit(self,jpeg):
        with self.lock:
            if self.enabled and jpeg and self.pending is None:self.pending=jpeg
    def _loop(self):
        import cv2,numpy as np
        interval=max(1.,float(getattr(settings,'FACE_RECOGNITION_INTERVAL',2.)))
        while not self.stop_event.is_set():
            start=time.monotonic()
            with self.lock:jpeg=self.pending;self.pending=None
            if jpeg:
                try:
                    img=cv2.imdecode(np.frombuffer(jpeg,dtype=np.uint8),cv2.IMREAD_COLOR)
                    if img is not None:
                        h,w=img.shape[:2];scale=min(1.,float(getattr(settings,'FACE_RECOGNITION_WIDTH',320))/max(w,1))
                        if scale<1:img=cv2.resize(img,(max(1,round(w*scale)),max(1,round(h*scale))))
                        h,w=img.shape[:2];self.detector.setInputSize((w,h));_,detected=self.detector.detect(img)
                        found=[]
                        for face in detected if detected is not None else []:
                            name='unknown';best=-1.
                            if self.known:
                                feature=self.recognizer.feature(self.recognizer.alignCrop(img,face))
                                for label,ref in self.known:
                                    score=float(self.recognizer.match(feature,ref,cv2.FaceRecognizerSF_FR_COSINE))
                                    if score>best:best=score;name=label
                                if best<float(getattr(settings,'FACE_RECOGNITION_THRESHOLD',0.45)):name='unknown'
                            x,y,bw,bh=map(float,face[:4]);x=max(0,min(w,x));y=max(0,min(h,y))
                            found.append({'x':x/w,'y':y/h,'w':max(0,min(w-x,bw))/w,'h':max(0,min(h-y,bh))/h,'name':name})
                        with self.lock:
                            if self.enabled:self.faces=found;self.updated_at=time.time();self.error=None
                except Exception as exc:
                    with self.lock:self.error=str(exc);self.faces=[]
            self.stop_event.wait(max(0.,interval-(time.monotonic()-start)))
        with self.lock:
            self.detector=None;self.recognizer=None;self.known=[];self.pending=None
    def status(self):
        with self.lock:
            return {'enabled':self.enabled,'faces':list(self.faces),'updated_at':self.updated_at,'known_people':sorted(set(n for n,_ in self.known)),'error':self.error,'interval':float(getattr(settings,'FACE_RECOGNITION_INTERVAL',2.))}

vision=FaceVision()
