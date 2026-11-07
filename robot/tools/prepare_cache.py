"""Prepare only expensive reusable assets; run: python -m robot.tools.prepare_cache."""
import argparse,time
from pathlib import Path
from robot.assets.assets import assets
from robot.tools.shell_cache import prepare
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--force",action="store_true",help="Remove shell caches before rebuilding")
    args=parser.parse_args();start=time.perf_counter()
    entries=assets.available("shell");ready=updated=failed=0
    if args.force:
        from robot.tools.shell_cache import CACHE
        for p in CACHE.glob("*.stc"):p.unlink()
    for name,item in entries.items():
        path=item.get("path")
        if not path or Path(path).suffix.lower() not in (".gif",".png",".jpg",".jpeg",".webp"):continue
        try:
            _,changed=prepare(path,320,480,item.get("rotation",0),item.get("resize",True))
            updated+=int(changed);ready+=int(not changed)
        except Exception as error:failed+=1;print(f"[CACHE] shell {name}: ERROR {error}")
    print(f"[CACHE] Shell: {ready} ready, {updated} updated, {failed} failed ({time.perf_counter()-start:.1f}s)")
    try:
        import cv2
        from robot.tools.vision_cache import ROOT,load_or_build
        models=ROOT/'robot'/'assets'/'models'
        detector_path=models/'face_detection_yunet_2023mar.onnx';recognizer_path=models/'face_recognition_sface_2021dec.onnx'
        if detector_path.is_file() and recognizer_path.is_file():
            detector=cv2.FaceDetectorYN.create(str(detector_path),'',(320,320))
            recognizer=cv2.FaceRecognizerSF.create(str(recognizer_path),'')
            refs,skipped,hit=load_or_build(detector,recognizer,[detector_path,recognizer_path],ROOT/'robot'/'assets'/'faces')
            print(f"[CACHE] Vision: {len(refs)} embeddings, {skipped} skipped, {'ready' if hit else 'updated'}")
        else:print("[CACHE] Vision: models unavailable, skipped")
    except ImportError:print("[CACHE] Vision: OpenCV unavailable, skipped")
    except Exception as error:failed+=1;print(f"[CACHE] Vision: ERROR {error}")
    print("[CACHE] Speech: existing on-demand Piper cache retained; eyes/LED: not precached (no proven bottleneck)")
    if failed:raise SystemExit(1)
if __name__=="__main__":main()
