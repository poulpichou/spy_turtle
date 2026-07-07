function startMove(direction){
    sendCommand("move",direction);
}

function stopMove(){
    sendCommand("move","stop");
}


function setupMovementButton(id,direction){

    const button=document.getElementById(id);

    button.addEventListener(
        "mousedown",
        ()=>{
            startMove(direction);
        }
    );

    button.addEventListener(
        "mouseup",
        ()=>{
            stopMove();
        }
    );

    button.addEventListener(
        "mouseleave",
        ()=>{
            stopMove();
        }
    );


    button.addEventListener(
        "touchstart",
        (event)=>{
            event.preventDefault();
            startMove(direction);
        }
    );


    button.addEventListener(
        "touchend",
        ()=>{
            stopMove();
        }
    );

}


setupMovementButton(
    "forward",
    "forward"
);

setupMovementButton(
    "backward",
    "backward"
);

setupMovementButton(
    "left",
    "left"
);

setupMovementButton(
    "right",
    "right"
);


document
.getElementById("stop")
.onclick=function(){
    stopMove();
};