const tabs=[...document.querySelectorAll(".center-tab")];
const views=[...document.querySelectorAll(".center-view")];
const logElement=document.getElementById("robot-log");
const photoPreview=document.getElementById("photo-preview");
const photoEmpty=document.getElementById("photo-empty");
const photoName=document.getElementById("photo-name");
let activeView="camera";
let logTimer=null;
let healthTimer=null;
let photos=[];
let photoIndex=0;

function setCenterView(name){
    if(name===activeView)return;
    activeView=name;
    tabs.forEach(tab=>tab.classList.toggle("active",tab.dataset.view===name));
    views.forEach(view=>view.classList.toggle("active",view.id===`${name}-view`));
    stopLogs();
    stopHealth();
    if(name==="camera")startCameraRefresh();
    else{
        stopCameraRefresh();
        if(name==="logs")startLogs();
        else if(name==="photos")loadPhotos();
        else if(name==="status")startHealth();
    }
}

tabs.forEach(tab=>tab.addEventListener("click",event=>{
    event.preventDefault();
    event.stopPropagation();
    setCenterView(tab.dataset.view);
}));

async function refreshLogs(){
    try{
        const response=await fetch("/logs?count=80",{cache:"no-store"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const data=await response.json();
        logElement.textContent=data.lines.join("\n")||"No logs yet";
        logElement.scrollTop=logElement.scrollHeight;
    }catch(error){
        logElement.textContent=`Unable to load logs: ${error.message}`;
    }
}

function startLogs(){
    refreshLogs();
    if(!logTimer)logTimer=setInterval(refreshLogs,1000);
}

function stopLogs(){
    if(!logTimer)return;
    clearInterval(logTimer);
    logTimer=null;
}

async function loadPhotos(){
    try{
        const response=await fetch("/photos",{cache:"no-store"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const data=await response.json();
        photos=data.photos||[];
        photoIndex=Math.min(photoIndex,Math.max(0,photos.length-1));
        showPhoto();
    }catch(error){
        photos=[];
        showPhoto();
        photoEmpty.textContent=`Unable to load photos: ${error.message}`;
    }
}

function showPhoto(){
    const photo=photos[photoIndex];
    photoPreview.style.display=photo?"block":"none";
    photoEmpty.style.display=photo?"none":"block";
    photoName.textContent=photo?`${photoIndex+1}/${photos.length} · ${photo.name}`:"";
    if(photo)photoPreview.src=`${photo.url}?t=${Date.now()}`;
}

document.getElementById("photo-previous").onclick=()=>{
    if(!photos.length)return;
    photoIndex=(photoIndex-1+photos.length)%photos.length;
    showPhoto();
};

document.getElementById("photo-next").onclick=()=>{
    if(!photos.length)return;
    photoIndex=(photoIndex+1)%photos.length;
    showPhoto();
};

document.getElementById("photo-button").onclick=async()=>{
    try{
        const response=await fetch("/photos/capture",{method:"POST"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        if(activeView==="photos")await loadPhotos();
    }catch(error){
        showCommandError(error);
    }
};

function formatDuration(seconds){
    seconds=Math.max(0,Math.floor(seconds||0));
    const days=Math.floor(seconds/86400);
    const hours=Math.floor((seconds%86400)/3600);
    const minutes=Math.floor((seconds%3600)/60);
    if(days)return `${days}d ${hours}h`;
    if(hours)return `${hours}h ${minutes}m`;
    return `${minutes}m ${seconds%60}s`;
}

function valueOrDash(value,suffix=""){
    return value===null||value===undefined?"--":`${value}${suffix}`;
}

function formatServo(axis){
    if(!axis)return "--";
    const current=valueOrDash(axis.current,"°");
    const target=valueOrDash(axis.target,"°");
    return `${current} → ${target}`;
}

async function refreshHealth(){
    try{
        const response=await fetch("/health",{cache:"no-store"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const data=await response.json();
        document.getElementById("health-connection").innerText="Connected";
        document.getElementById("health-uptime").innerText=formatDuration(data.system.uptime_seconds);
        document.getElementById("health-temperature").innerText=valueOrDash(data.system.cpu_temperature_c," °C");
        document.getElementById("health-load").innerText=valueOrDash(data.system.load_1m);
        document.getElementById("health-disk").innerText=valueOrDash(data.system.disk_free_gb," GB");
        document.getElementById("health-voltage").innerText=valueOrDash(data.battery.voltage_v," V");
        document.getElementById("health-current").innerText=valueOrDash(data.battery.current_a," A");
        document.getElementById("health-cells").innerText=valueOrDash(data.battery.cells);
        document.getElementById("health-charging").innerText=data.battery.charging===null?"--":data.battery.charging?"Yes":"No";
        document.getElementById("health-usb").innerText=data.battery.usb_connected===null?"--":data.battery.usb_connected?"Connected":"No";
        document.getElementById("health-idle").innerText=formatDuration(data.robot.idle_seconds);
        document.getElementById("health-mode").innerText=`${data.robot.motion} / ${data.robot.emotion}`;
        document.getElementById("health-pan").innerText=formatServo(data.robot.servo?.pan);
        document.getElementById("health-tilt").innerText=formatServo(data.robot.servo?.tilt);
    }catch(error){
        document.getElementById("health-connection").innerText="Offline";
        document.getElementById("health-pan").innerText="--";
        document.getElementById("health-tilt").innerText="--";
    }
}

function startHealth(){
    refreshHealth();
    if(!healthTimer)healthTimer=setInterval(refreshHealth,3000);
}

function stopHealth(){
    if(!healthTimer)return;
    clearInterval(healthTimer);
    healthTimer=null;
}
