function startMove(direction){sendCommand("move",direction)}
function stopMove(){sendCommand("move","stop")}

function setupMovementButton(id,direction){
    const b=document.getElementById(id);
    b.addEventListener("mousedown",()=>startMove(direction));
    b.addEventListener("mouseup",stopMove);
    b.addEventListener("mouseleave",stopMove);
    b.addEventListener("touchstart",e=>{e.preventDefault();startMove(direction)});
    b.addEventListener("touchend",stopMove);
}

setupMovementButton("forward","forward");
setupMovementButton("backward","backward");
setupMovementButton("left","left");
setupMovementButton("right","right");

document.getElementById("stop").onclick=stopMove;

function setupHeadButton(id,direction){
    document.getElementById(id).onclick=()=>sendCommand("head",direction);
}

setupHeadButton("head-left","left");
setupHeadButton("head-right","right");
setupHeadButton("head-up","up");
setupHeadButton("head-down","down");
setupHeadButton("head-center","center");

document.getElementById("face-select").onchange=e=>{
    console.log("FACE:",e.target.value);
    sendCommand("face",e.target.value);
};

document.getElementById("shell-select").onchange=e=>{
    console.log("SHELL:",e.target.value);
    sendCommand("shell",e.target.value);
};

document.getElementById("led-select").onchange=e=>{
    console.log("LED:",e.target.value);
    sendCommand("led",e.target.value);
};