const connectionIcon=document.getElementById('connection-icon');
const connectionText=document.getElementById('connection');
const DASHBOARD_NORMAL_MS=1000;
const DASHBOARD_IDLE_MS=5000;
let lastConnectedAt=0;
let dashboardTimer=null;
let dashboardIdle=false;

function setConnection(status){
    connectionIcon.className=`connection-dot ${status}`;
    connectionText.innerText=status==='connected'?'Connected':status==='connecting'?'Connecting':'Offline';
}

function scheduleDashboard(delay=null){
    if(dashboardTimer)clearTimeout(dashboardTimer);
    dashboardTimer=setTimeout(updateDashboard,delay??(dashboardIdle?DASHBOARD_IDLE_MS:DASHBOARD_NORMAL_MS));
}

function setDashboardIdle(idle){
    dashboardIdle=!!idle;
    scheduleDashboard(0);
}

async function updateDashboard(){
    try{
        const status=await getStatus();
        const battery=status.battery||{};
        lastConnectedAt=Date.now();
        setConnection('connected');
        document.getElementById('battery').innerText=battery.level===null||battery.level===undefined?'--':Math.round(battery.level);
        document.getElementById('battery-status').innerText=battery.status||'unknown';
        document.getElementById('emotion').innerText=status.brain?.emotion||'neutral';
        document.getElementById('shell-mode').innerText=status.shell?.mode||'status';
        document.getElementById('led-mode').innerText=status.leds?.mode||'off';
        document.getElementById('motion').innerText=status.motion?.state||'stop';
    }catch(error){setConnection('disconnected')}
    scheduleDashboard();
}

setConnection('connecting');
scheduleDashboard(0);
