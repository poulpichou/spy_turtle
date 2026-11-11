const tabs=[...document.querySelectorAll(".center-tab")];
const views=[...document.querySelectorAll(".center-view")];
const logElement=document.getElementById("robot-log");
const photoPreview=document.getElementById("photo-preview");
const photoEmpty=document.getElementById("photo-empty");
const photoName=document.getElementById("photo-name");
let activeView="camera";
let thermalTimer=null;
let logTimer=null;
let healthTimer=null;
let photos=[];
let photoIndex=0;
let photoToken=0,photoObjectUrl=null;

function stopThermal(){if(thermalTimer){clearInterval(thermalTimer);thermalTimer=null;}if(transportMode==="bluetooth")document.getElementById("thermal-stream").removeAttribute("src");}
function startThermal(){
    if(transportMode==="bluetooth"){document.getElementById("thermal-stream").alt="Bluetooth thermal stream";return;}
    const refresh=()=>document.getElementById("thermal-stream").src=`/thermal/frame?t=${Date.now()}`;
    refresh();
    thermalTimer=setInterval(refresh,500);
}

function setCenterView(name){
    if(name===activeView)return;
    activeView=name;
    if(name!=="photos")photoToken++;
    tabs.forEach(tab=>tab.classList.toggle("active",tab.dataset.view===name));
    views.forEach(view=>view.classList.toggle("active",view.id===`${name}-view`));
    stopLogs();
    stopHealth();
    stopThermal();
    if(name==="camera")startCameraRefresh();
    else{
        stopCameraRefresh();
        if(name==="thermal")startThermal();
        else if(name==="logs")startLogs();
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
    if(transportMode==="bluetooth"){
        try{
            const level=localStorage.getItem("spy_log_level")||"INFO";
            const result=await bluetoothAdminRequest("log_tail",{level});
            logElement.textContent=(result.lines||[]).join("\n")||"No recent logs";
            logElement.scrollTop=logElement.scrollHeight;
        }catch(error){logElement.textContent=`Bluetooth logs unavailable: ${error.message}`;}
        return;
    }
    try{
        const response=await fetch(`/logs?count=80&level=${encodeURIComponent(localStorage.getItem("spy_log_level")||"INFO")}`,{cache:"no-store"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const data=await response.json();
        logElement.textContent=data.lines.join("\n")||"No logs yet";
        logElement.scrollTop=logElement.scrollHeight;
    }catch(error){logElement.textContent=`Unable to load logs: ${error.message}`;}
}
function startLogs(){refreshLogs();if(!logTimer)logTimer=setInterval(refreshLogs,transportMode==="bluetooth"?2500:1000);}
function stopLogs(){if(!logTimer)return;clearInterval(logTimer);logTimer=null;}

async function loadPhotos(){
    if(transportMode==="bluetooth"){
        try{
            const entries=[];
            for(let offset=0;offset<60;offset+=3){
                const result=await bluetoothAdminRequest("photo_list",{offset});
                entries.push(...(result.items||[]));
                if(entries.length>=result.total||!(result.items||[]).length)break;
            }
            photos=entries.map(item=>({name:item.name}));
            photoIndex=Math.min(photoIndex,Math.max(0,photos.length-1));
            showPhoto();
        }catch(error){photos=[];showPhoto();photoEmpty.textContent=`Bluetooth photos unavailable: ${error.message}`;}
        return;
    }
    try{
        const response=await fetch("/photos",{cache:"no-store"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        photos=(await response.json()).photos||[];
        photoIndex=Math.min(photoIndex,Math.max(0,photos.length-1));
        showPhoto();
    }catch(error){
        photos=[];
        showPhoto();
        photoEmpty.textContent=`Unable to load photos: ${error.message}`;
    }
}
async function showPhoto(){
    const token=++photoToken,photo=photos[photoIndex];
    if(photoObjectUrl){URL.revokeObjectURL(photoObjectUrl);photoObjectUrl=null;}
    photoPreview.removeAttribute("src");
    photoPreview.style.display=photo?"block":"none";
    photoEmpty.style.display=photo?"none":"block";
    photoName.textContent=photo?`${photoIndex+1}/${photos.length} · ${photo.name}`:"";
    if(!photo)return;
    if(transportMode!=="bluetooth"){photoPreview.src=`${photo.url}?t=${Date.now()}`;return;}
    photoName.textContent+= " · Loading Bluetooth preview...";
    try{
        const blob=await blePhotoFetch(photo.name);
        if(token!==photoToken||activeView!=="photos"||transportMode!=="bluetooth")return;
        photoObjectUrl=URL.createObjectURL(blob);photoPreview.src=photoObjectUrl;
        photoName.textContent=`${photoIndex+1}/${photos.length} · ${photo.name}`;
    }catch(error){if(token===photoToken)photoName.textContent=`${photo.name} · ${error.message}`;}
}
document.getElementById("photo-previous").onclick=()=>{if(!photos.length)return;photoIndex=(photoIndex-1+photos.length)%photos.length;showPhoto();};
document.getElementById("photo-next").onclick=()=>{if(!photos.length)return;photoIndex=(photoIndex+1)%photos.length;showPhoto();};
document.getElementById("photo-button").onclick=async()=>{
    try{
        if(transportMode==="bluetooth")await bluetoothAdminRequest("photo_capture",{source:"camera"});
        else{const response=await fetch("/photos/capture",{method:"POST"});if(!response.ok)throw new Error(`HTTP ${response.status}`)}
        if(activeView==="photos")await loadPhotos();
    }catch(error){showCommandError(error);}
};

function formatDuration(seconds){
    seconds=Math.max(0,Math.floor(seconds||0));
    const days=Math.floor(seconds/86400),hours=Math.floor((seconds%86400)/3600),minutes=Math.floor((seconds%3600)/60);
    if(days)return `${days}d ${hours}h`;
    if(hours)return `${hours}h ${minutes}m`;
    return `${minutes}m ${seconds%60}s`;
}
function valueOrDash(value,suffix=""){return value===null||value===undefined?"--":`${value}${suffix}`;}
function formatServo(axis){return axis?`${valueOrDash(axis.current,"°")} → ${valueOrDash(axis.target,"°")}`:"--";}
async function fetchJson(url){
    const response=await fetch(`${url}${url.includes("?")?"&":"?"}t=${Date.now()}`,{cache:"no-store"});
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    return response.json();
}
async function refreshHealth(){
    if(transportMode==="bluetooth"){
        try{
            const state=await readBluetoothState();
            const env=state.sensors?.environment||{},dist=state.sensors?.distance||{},battery=state.battery||{};
            const values={"health-object-distance":dist.distance_mm==null?"--":dist.out_of_range?"∞":`${dist.distance_mm} mm`,"health-environment-temperature":valueOrDash(env.temperature_c," °C"),"health-humidity":valueOrDash(env.humidity_percent," %"),"health-pressure":valueOrDash(env.pressure_hpa," hPa"),"health-pressure-atm":valueOrDash(env.pressure_atm," atm"),"health-gas":env.gas_ohms==null?"--":`${(env.gas_ohms/1000).toFixed(1)} kΩ`,"health-air-quality":valueOrDash(env.air_quality," / 10"),"health-level":valueOrDash(battery.level,"%"),"health-battery-status":battery.status||"unknown","health-charging":battery.charging==null?"--":battery.charging?"Yes":"No","health-mode":`${state.motion?.state||"stop"} / ${state.brain?.emotion||"neutral"}`,"health-pan":formatServo(state.servo?.pan),"health-tilt":formatServo(state.servo?.tilt),"health-connection":"Bluetooth"};
            for(const [id,value] of Object.entries(values))document.getElementById(id).textContent=value;
            for(const id of ["health-uptime","health-temperature","health-load","health-disk","health-voltage","health-current","health-power","health-cells","health-usb","health-battery-error","health-idle","health-detected-recent","health-ambient-sound","health-ambient-rms","health-adaptive-boost"])document.getElementById(id).textContent="--";
        }catch(error){document.getElementById("health-connection").textContent="Bluetooth disconnected";}
        return;
    }
    try{
        const data=await fetchJson("/health");
        const robotState=await fetchJson("/state");
        const names=(robotState.vision?.detected_recent||[]).map(person=>person.name).filter(Boolean);
        const allNames=names.join(", ")||"None";
        const recentElement=document.getElementById("health-detected-recent");
        recentElement.textContent=allNames.length>25?allNames.slice(0,22)+"...":allNames;
        recentElement.title=allNames;
        let servo=data.robot?.servo;
        if(!servo)servo=robotState.servo;
        const distance=data.sensors?.distance?.distance_mm;
        const environment=data.sensors?.environment||{};
        document.getElementById("health-object-distance").innerText=distance==null?"--":data.sensors?.distance?.out_of_range?"∞":`${distance} mm`;
        document.getElementById("health-environment-temperature").innerText=valueOrDash(environment.temperature_c," °C");
        document.getElementById("health-humidity").innerText=valueOrDash(environment.humidity_percent," %");
        document.getElementById("health-pressure").innerText=valueOrDash(environment.pressure_hpa," hPa");
        document.getElementById("health-pressure-atm").innerText=valueOrDash(environment.pressure_atm," atm");
        document.getElementById("health-gas").innerText=environment.gas_ohms==null?"--":`${(environment.gas_ohms/1000).toFixed(1)} kΩ`;
        document.getElementById("health-air-quality").innerText=valueOrDash(environment.air_quality," / 10");
        document.getElementById("health-connection").innerText="Connected";
        document.getElementById("health-uptime").innerText=formatDuration(data.system.uptime_seconds);
        document.getElementById("health-temperature").innerText=valueOrDash(data.system.cpu_temperature_c," °C");
        document.getElementById("health-load").innerText=valueOrDash(data.system.load_1m);
        document.getElementById("health-disk").innerText=valueOrDash(data.system.disk_free_gb," GB");
        document.getElementById("health-level").innerText=valueOrDash(data.battery.level,"%");
        document.getElementById("health-battery-status").innerText=data.battery.status||"unknown";
        document.getElementById("health-voltage").innerText=valueOrDash(data.battery.voltage_v," V");
        document.getElementById("health-current").innerText=valueOrDash(data.battery.current_a," A");
        document.getElementById("health-power").innerText=valueOrDash(data.battery.power_w," W");
        document.getElementById("health-cells").innerText=data.battery.cells_mv?.length?data.battery.cells_mv.map(value=>(value/1000).toFixed(3)).join(" / "):"--";
        document.getElementById("health-charging").innerText=data.battery.charging===null?"--":data.battery.charging?"Yes":"No";
        document.getElementById("health-battery-error").innerText=data.battery.error||"None";
        document.getElementById("health-usb").innerText=data.battery.usb_connected===null?"--":data.battery.usb_connected?"Connected":"No";
        document.getElementById("health-idle").innerText=formatDuration(data.robot.brain?.idle_seconds);
        document.getElementById("health-mode").innerText=`${data.robot.motion?.state||"stop"} / ${data.robot.brain?.emotion||"neutral"}`;
        document.getElementById("health-pan").innerText=formatServo(servo?.pan);
        document.getElementById("health-tilt").innerText=formatServo(servo?.tilt);
    }catch(error){
        document.getElementById("health-connection").innerText="Offline";document.getElementById("health-detected-recent").innerText="--";
        document.getElementById("health-pan").innerText="--";
        document.getElementById("health-tilt").innerText="--";
    }
}
function startHealth(){refreshHealth();if(!healthTimer)healthTimer=setInterval(refreshHealth,1000);}
function stopHealth(){if(!healthTimer)return;clearInterval(healthTimer);healthTimer=null;}
document.addEventListener("transportchange",()=>{
    photoToken++;if(photoObjectUrl){URL.revokeObjectURL(photoObjectUrl);photoObjectUrl=null;}
    stopLogs();stopHealth();stopThermal();
    if(activeView==="thermal")startThermal();
    else if(activeView==="logs")startLogs();
    else if(activeView==="photos")loadPhotos();
    else if(activeView==="status")startHealth();
});
