const connectionIcon=document.getElementById('connection-icon');
const connectionText=document.getElementById('connection');
let lastConnectedAt=0;

function setConnection(status){
    connectionIcon.className=`connection-dot ${status}`;
    connectionText.innerText=status==='connected'?'Connected':status==='connecting'?'Connecting':'Offline';
}

async function updateDashboard(){
    try{
        const controller=new AbortController();
        const timeout=setTimeout(()=>controller.abort(),2000);
        const response=await fetch('/state',{cache:'no-store',signal:controller.signal});
        clearTimeout(timeout);
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const status=await response.json();
        const battery=status.battery||{};
        lastConnectedAt=Date.now();
        setConnection('connected');
        document.getElementById('battery').innerText=battery.level===null||battery.level===undefined?'--':Math.round(battery.level);
        document.getElementById('battery-status').innerText=battery.status||'unknown';
        document.getElementById('emotion').innerText=status.brain?.emotion||'neutral';
        document.getElementById('shell-mode').innerText=status.shell?.mode||'status';
        document.getElementById('led-mode').innerText=status.leds?.mode||'off';
        document.getElementById('motion').innerText=status.motion?.state||'stop';
    }catch(error){setConnection('disconnected');}
}

setConnection('connecting');
setInterval(updateDashboard,1000);
updateDashboard();
