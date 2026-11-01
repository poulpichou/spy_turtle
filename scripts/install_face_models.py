from pathlib import Path
from urllib.request import urlretrieve
root=Path(__file__).resolve().parents[1]/'robot/assets/models';root.mkdir(parents=True,exist_ok=True)
models={
'face_detection_yunet_2023mar.onnx':'https://raw.githubusercontent.com/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx',
'face_recognition_sface_2021dec.onnx':'https://raw.githubusercontent.com/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx'}
for name,url in models.items():
    target=root/name
    if not target.exists():print('Downloading',name);urlretrieve(url,target)
    if target.stat().st_size<100000:raise RuntimeError(f'Invalid model: {target}')
print('Face models ready')
