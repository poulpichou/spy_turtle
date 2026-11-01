const camera=document.getElementById("camera-stream");
let cameraTimer=null;
let cameraFps=Math.max(2,Math.min(10,Number(localStorage.getItem("spy_turtle_camera_fps"))||6));
function updateCamera(){if(transportMode==="bluetooth"||!document.getElementById("camera-view").classList.contains("active"))return;camera.src="/camera/frame?t="+Date.now()}
function startCameraRefresh(){if(transportMode==="bluetooth")return;if(cameraTimer)return;updateCamera();cameraTimer=setInterval(updateCamera,Math.round(1000/cameraFps))}
function stopCameraRefresh(){if(!cameraTimer)return;clearInterval(cameraTimer);cameraTimer=null}
function setCameraFps(fps){cameraFps=Math.max(2,Math.min(10,Number(fps)||6));localStorage.setItem("spy_turtle_camera_fps",String(cameraFps));const running=!!cameraTimer;if(running){stopCameraRefresh();startCameraRefresh()}return cameraFps}
function getCameraFps(){return cameraFps}
startCameraRefresh();

// BLE camera: JPEG frames are assembled from small GATT reads; Wi-Fi stream remains unchanged.
let bleCameraRunning=false,bleCameraUrl=null,bleCameraErrors=0;
async function bleCameraLoop(){
    if(bleCameraRunning)return;
    bleCameraRunning=true;
    try{
        while(transportMode==="bluetooth"&&bluetoothServer?.connected){
            if(!document.getElementById("camera-view").classList.contains("active")){
                await new Promise(resolve=>setTimeout(resolve,400));continue;
            }
            try{
                const blob=await readBluetoothCameraFrame();
                if(transportMode!=="bluetooth")break;
                const url=URL.createObjectURL(blob),previous=bleCameraUrl;
                bleCameraUrl=url;camera.src=url;
                if(previous)URL.revokeObjectURL(previous);
                bleCameraErrors=0;
            }catch(error){
                if(transportMode!=="bluetooth")break;
                console.warn("[BLE CAMERA]",error);
                bleCameraErrors++;
                if(bleCameraErrors>=3){camera.removeAttribute("src");camera.alt="Bluetooth camera unavailable"}
                await new Promise(resolve=>setTimeout(resolve,1500));
            }
            // Maximum 3 FPS; actual throughput depends on MTU and signal.
            await new Promise(resolve=>setTimeout(resolve,333));
        }
    }finally{bleCameraRunning=false}
}
document.addEventListener("transportchange",()=>{
    if(transportMode==="bluetooth"){
        stopCameraRefresh();camera.removeAttribute("src");bleCameraLoop();
    }else{
        if(bleCameraUrl){URL.revokeObjectURL(bleCameraUrl);bleCameraUrl=null}
        camera.src="/camera/frame?t="+Date.now();startCameraRefresh();
    }
});
