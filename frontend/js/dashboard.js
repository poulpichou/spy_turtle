const connectionIcon=document.getElementById("connection-icon");
const connectionText=document.getElementById("connection");
let lastConnectedAt=0;

function setConnection(status){
    connectionIcon.className=`connection-dot ${status}`;
    connectionText.innerText=status==="connected"?"Connected":status==="connecting"?"Connecting":"Offline";
}

async function updateDashboard(){
    try{
        const controller=new AbortController();
        const timeout=setTimeout(()=>controller.abort(),2000);
        const response=await fetch("/state",{cache:"no-store",signal:controller.signal});
        clearTimeout(timeout);
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const status=await response.json();
        lastConnectedAt=Date.now();
        setConnection("connected");
        document.getElementById("battery").innerText=Math.round(status.battery??0);
        document.getElementById("emotion").innerText=status.emotion||"neutral";
        document.getElementById("shell-mode").innerText=status.shell_mode||"status";
        document.getElementById("led-mode").innerText=status.led_mode||"off";
        document.getElementById("motion").innerText=status.motion||"stop";
    }catch(error){
        setConnection("disconnected");
    }
}

setConnection("connecting");
setInterval(updateDashboard,1000);
updateDashboard();
