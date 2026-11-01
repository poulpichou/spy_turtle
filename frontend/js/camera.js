const camera=document.getElementById("camera-stream");
const cameraView=document.getElementById("camera-view");
const cameraBuffer=document.createElement("img");cameraBuffer.id="camera-buffer";cameraBuffer.alt="";cameraBuffer.setAttribute("aria-hidden","true");camera.after(cameraBuffer);
for(const img of [camera,cameraBuffer]){img.style.position="absolute";img.style.inset="0";img.style.width="100%";img.style.height="100%";img.style.objectFit="contain";img.style.background="#080808"}
camera.style.visibility="visible";cameraBuffer.style.visibility="hidden";
let cameraActive=camera,cameraTimer=null,cameraLoading=false,cameraFps=Math.max(2,Math.min(10,Number(localStorage.getItem("spy_turtle_camera_fps"))||6));
function updateCamera(){
    if(cameraLoading||!cameraView.classList.contains("active"))return;
    cameraLoading=true;
    const next=cameraActive===camera?cameraBuffer:camera;
    next.onload=()=>{next.style.visibility="visible";cameraActive.style.visibility="hidden";cameraActive=next;cameraLoading=false;window.dispatchEvent(new Event("spy-camera-frame"))};
    next.onerror=()=>{cameraLoading=false};
    next.src="/camera/frame?t="+Date.now();
}
function startCameraRefresh(){if(cameraTimer)return;updateCamera();cameraTimer=setInterval(updateCamera,Math.round(1000/cameraFps))}
function stopCameraRefresh(){if(!cameraTimer)return;clearInterval(cameraTimer);cameraTimer=null}
function setCameraFps(fps){cameraFps=Math.max(2,Math.min(10,Number(fps)||6));localStorage.setItem("spy_turtle_camera_fps",String(cameraFps));const running=!!cameraTimer;if(running){stopCameraRefresh();startCameraRefresh()}return cameraFps}
function getCameraFps(){return cameraFps}
startCameraRefresh();
