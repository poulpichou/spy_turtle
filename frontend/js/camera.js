const camera=document.getElementById("camera-stream");

function updateCamera(){
    camera.src="/camera/frame?t="+Date.now();
}

setInterval(updateCamera,500);
updateCamera();