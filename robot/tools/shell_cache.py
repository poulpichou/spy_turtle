"""Precompiled RGB565 shell assets, validated by source metadata and render parameters."""
import hashlib,json,struct,time
from pathlib import Path
from PIL import Image,ImageSequence
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/"cache"/"shell"
VERSION=2
def cache_path(source,width,height,rotation,resize):
    source=Path(source).resolve();stat=source.stat()
    key=json.dumps([VERSION,str(source),stat.st_size,stat.st_mtime_ns,width,height,rotation,bool(resize)])
    return CACHE/(hashlib.sha256(key.encode()).hexdigest()+".stc")
def _frame(image,width,height,rotation,resize):
    import numpy as np
    image=image.convert("RGB")
    if rotation:image=image.rotate(rotation,expand=True)
    if resize:image.thumbnail((width,height))
    canvas=Image.new("RGB",(width,height))
    canvas.paste(image,((width-image.width)//2,(height-image.height)//2))
    a=np.asarray(canvas,dtype=np.uint8);v=((a[:,:,0].astype(np.uint16)&248)<<8)|((a[:,:,1].astype(np.uint16)&252)<<3)|(a[:,:,2].astype(np.uint16)>>3)
    return v.astype(">u2").tobytes()
def prepare(source,width=320,height=480,rotation=0,resize=True):
    source=Path(source);target=cache_path(source,width,height,rotation,resize)
    if target.is_file() and target.stat().st_size>64:return target,False
    CACHE.mkdir(parents=True,exist_ok=True);tmp=target.with_suffix(".part")
    started=time.perf_counter()
    try:
        with Image.open(source) as img:
            frames=[];durations=[]
            for frame in ImageSequence.Iterator(img):
                frames.append(_frame(frame,width,height,rotation,resize))
                durations.append(max(0.05,float(frame.info.get("duration",100))/1000))
            if not frames:raise ValueError("Empty image")
        header=json.dumps({"version":VERSION,"width":width,"height":height,"frames":len(frames),"durations":durations}).encode()
        with tmp.open("wb") as out:
            out.write(b"STC2");out.write(struct.pack("<I",len(header)));out.write(header)
            for frame in frames:out.write(frame)
        tmp.replace(target)
        print(f"[CACHE] shell {source.name}: {len(frames)} frames, {target.stat().st_size/1048576:.1f} MiB, {time.perf_counter()-started:.2f}s")
    finally:tmp.unlink(missing_ok=True)
    return target,True
class Reader:
    def __init__(self,path):
        self.file=open(path,"rb")
        try:
            if self.file.read(4)!=b"STC2":raise ValueError("Bad shell cache")
            n=struct.unpack("<I",self.file.read(4))[0]
            if not 0<n<100000:raise ValueError("Invalid cache header")
            header=json.loads(self.file.read(n))
            if header["version"]!=VERSION:raise ValueError("Cache version")
            self.width=int(header["width"]);self.height=int(header["height"])
            self.count=int(header["frames"]);self.durations=header["durations"]
            self.offset=self.file.tell();self.frame_size=self.width*self.height*2
            if Path(path).stat().st_size!=self.offset+self.frame_size*self.count:raise ValueError("Truncated shell cache")
        except Exception:self.file.close();raise
    def read(self,index):
        self.file.seek(self.offset+(index%self.count)*self.frame_size)
        result=self.file.read(self.frame_size)
        if len(result)!=self.frame_size:raise IOError("Incomplete cached frame")
        return result
    def close(self):self.file.close()
