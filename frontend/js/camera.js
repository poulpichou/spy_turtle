const camera=document.getElementById("camera-stream");

if(camera){
    setInterval(()=>{
        camera.src="http://spyturtle:8000/camera/frame?"+Date.now();
    },500);
}