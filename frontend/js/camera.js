const camera=document.getElementById("camera-stream");

function updateCamera(){
    camera.src="http://spyturtle:8000/camera/frame?t="+Date.now();
}

setInterval(updateCamera,200);
updateCamera();