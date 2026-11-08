// [SHELL DIAG PATCH]
const adminResult=document.getElementById("admin-result");
(function(){
    const restart=document.querySelector('[data-admin-action="restart"]');
    if(!restart)return;
    const reset=document.createElement("button");reset.type="button";reset.textContent="Reset Turtle";restart.before(reset);
    reset.onclick=async()=>{
        if(!confirm("Reset Turtle controls without restarting the connection?"))return;
        reset.disabled=true;
        try{
            const response=await fetch("/admin/turtle/reset",{method:"POST"});
            const data=await response.json();
            adminResult.textContent=data.ok?"Turtle reset completed":"Reset partial: "+JSON.stringify(data.results);
        }catch(error){adminResult.textContent="Reset failed: "+error.message}
        finally{reset.disabled=false}
    };
})();
const volumeSlider=document.getElementById("volume-slider"),volumeValue=document.getElementById("volume-value");
const microSlider=document.getElementById("micro-slider"),microValue=document.getElementById("micro-value");const driveSpeedSlider=document.getElementById("drive-speed-slider"),driveSpeedValue=document.getElementById("drive-speed-value");const cameraFpsSlider=document.getElementById("camera-fps-slider"),cameraFpsValue=document.getElementById("camera-fps-value");
const idleToggle=document.getElementById("idle-toggle");
const powerButtons={back_screen:document.getElementById("back-screen-toggle"),eyes:document.getElementById("eyes-toggle"),shell_light:document.getElementById("shell-light-toggle")};
const powerSelects={back_screen:"shell-select",eyes:"face-select",shell_light:"led-select"};
const localFeatureButtons={animation:{button:document.getElementById("animation-toggle"),select:"animation-select",card:".animation-card",storage:"spy_turtle_animation_enabled"},sound:{button:document.getElementById("sound-toggle"),select:"sound-select",card:".sound-card",storage:"spy_turtle_sound_enabled"}};
const idleDirectionalIds=["forward","backward","left","right","stop","head-up","head-down","head-left","head-right","head-center"];
const idleControlIds=["photo-button","listen-button","record-message","screen-message-button"];
let runtimePower={idle_mode:false,back_screen:true,eyes:true,shell_light:true,microphone_sensitivity:60};
let localFeatures={animation:localStorage.getItem(localFeatureButtons.animation.storage)!=="false",sound:localStorage.getItem(localFeatureButtons.sound.storage)!=="false"};
let wifiTimer=null;

const bluetoothAdminActions={
    "/admin/turtle/restart":"restart","/admin/system/reboot":"reboot","/admin/system/shutdown":"shutdown",
    "/admin/wifi":"wifi_add","/admin/wifi/connect":"wifi_connect","/admin/wifi/delete":"wifi_delete",
    "/admin/audio/volume":"volume_set","/admin/power/component":"power_component","/admin/power/idle":"idle",
    "/admin/audio/microphone-sensitivity":"microphone_sensitivity","/admin/leds/brightness":"led_brightness_set",
    "/vision/enable":"vision_enable","/vision/interval":"vision_interval"
};
async function adminPost(path,body){
    if(transportMode==="bluetooth")return bluetoothAdminRequest(bluetoothAdminActions[path],body||{});
    const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):null});
    const text=await response.text(),data=text?JSON.parse(text):{ok:response.ok,message:"Command sent"};
    if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);
    return data;
}
async function adminGet(path){
    if(transportMode==="bluetooth"){
        if(path==="/admin/wifi")return bluetoothAdminRequest("wifi_status");
        if(path==="/admin/audio/volume")return bluetoothAdminRequest("volume_get");
        if(path==="/admin/power")return bluetoothAdminRequest("power_get");
        if(path==="/admin/leds/brightness")return bluetoothAdminRequest("led_brightness_get");
        throw new Error(`Unsupported Bluetooth admin GET: ${path}`);
    }
    const response=await fetch(path,{cache:"no-store"});
    const text=await response.text(),data=text?JSON.parse(text):{};
    if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);
    return data;
}
const ledBrightnessSlider=document.getElementById("led-brightness-slider"),ledBrightnessValue=document.getElementById("led-brightness-value");
function showLedBrightness(value){if(ledBrightnessValue)ledBrightnessValue.textContent=`${value}%`}
async function loadLedBrightness(){try{const data=await adminGet("/admin/leds/brightness");ledBrightnessSlider.value=data.brightness;showLedBrightness(data.brightness)}catch(error){console.warn("[LED BRIGHTNESS]",error)}}
if(ledBrightnessSlider){
    ledBrightnessSlider.oninput=()=>showLedBrightness(ledBrightnessSlider.value);
    ledBrightnessSlider.onchange=async()=>{try{const data=await adminPost("/admin/leds/brightness",{brightness:Number(ledBrightnessSlider.value)});showLedBrightness(data.brightness);adminResult.textContent=`LED intensity: ${data.brightness}%`}catch(error){adminResult.textContent=error.message}};
}
function showVolume(value){volumeValue.textContent=`${value}%`}
function showMicro(value){microValue.textContent=`${value}%`}function showDriveSpeed(value){driveSpeedValue.textContent=`${value}%`}function showCameraFps(value){cameraFpsValue.textContent=`${value} fps`}
function setSelectDisabled(id,disabled){
    const select=document.getElementById(id);if(!select)return;
    select.disabled=disabled;
    select.closest(".compact-select")?.classList.toggle("disabled",disabled);
}
function applyLocalFeature(name){
    const config=localFeatureButtons[name],enabled=localFeatures[name],idle=runtimePower.idle_mode;
    config.button.classList.toggle("active",enabled&&!idle);
    config.button.classList.toggle("off",!enabled||idle);
    config.button.disabled=idle;
    document.querySelector(config.card)?.classList.toggle("feature-disabled",!enabled||idle);
    setSelectDisabled(config.select,!enabled||idle);
}
function toggleLocalFeature(name){
    if(runtimePower.idle_mode)return;
    localFeatures[name]=!localFeatures[name];
    localStorage.setItem(localFeatureButtons[name].storage,String(localFeatures[name]));
    applyLocalFeature(name);
}
function applyPowerFeature(name,button){
    const enabled=!!runtimePower[name],idle=runtimePower.idle_mode,disabled=!enabled||idle;
    button.classList.toggle("active",enabled&&!idle);
    button.classList.toggle("off",disabled);
    button.disabled=idle;
    button.closest(".right-control")?.classList.toggle("feature-disabled",disabled);
    setSelectDisabled(powerSelects[name],disabled);
}
function applyPowerState(state){
    runtimePower={...runtimePower,...state};
    idleToggle.classList.toggle("active",runtimePower.idle_mode);
    idleToggle.querySelector("span").textContent="Idle";
    document.dispatchEvent(new CustomEvent("turtlepowerchange",{detail:{idle_mode:runtimePower.idle_mode}}));
    for(const [name,button] of Object.entries(powerButtons))applyPowerFeature(name,button);
    idleDirectionalIds.forEach(id=>{const button=document.getElementById(id);if(button)button.disabled=runtimePower.idle_mode});
    idleControlIds.forEach(id=>{const element=document.getElementById(id);if(element)element.disabled=runtimePower.idle_mode});
    applyLocalFeature("animation");applyLocalFeature("sound");
    microSlider.value=runtimePower.microphone_sensitivity??60;showMicro(microSlider.value);
    if(typeof setDashboardIdle==="function")setDashboardIdle(runtimePower.idle_mode);
    if(runtimePower.idle_mode){stopCameraRefresh();stopThermal()}
    else if(typeof activeView!=="undefined"){
        if(activeView==="camera")startCameraRefresh();
        else if(activeView==="thermal"&&!thermalTimer)startThermal();
    }
    scheduleWifi();
}
async function loadPower(){try{applyPowerState(await adminGet("/admin/power"))}catch(error){console.error("[POWER]",error)}}
async function loadVolume(){try{const data=await adminGet("/admin/audio/volume");volumeSlider.value=data.volume;showVolume(data.volume)}catch(error){console.error("[VOLUME]",error)}}async function loadDriveSpeed(){try{const data=await adminGet("/admin/motors/speed");driveSpeedSlider.value=data.speed;showDriveSpeed(data.speed)}catch(error){console.error("[MOTOR SPEED]",error)}}function loadCameraFps(){const fps=getCameraFps();cameraFpsSlider.value=fps;showCameraFps(fps)}

document.querySelectorAll("[data-admin-action]").forEach(button=>button.onclick=async()=>{
    const action=button.dataset.adminAction,labels={restart:"restart Spy Turtle",reboot:"reboot the Raspberry Pi",shutdown:"shut down the Raspberry Pi"};
    if(!confirm(`Really ${labels[action]}?`))return;
    try{adminResult.textContent=(await adminPost(action==="restart"?"/admin/turtle/restart":`/admin/system/${action}`)).message}
    catch(error){adminResult.textContent=["restart","reboot","shutdown"].includes(action)?"Command sent":error.message}
});
volumeSlider.oninput=()=>showVolume(volumeSlider.value);
volumeSlider.onchange=async()=>{try{const data=await adminPost("/admin/audio/volume",{volume:Number(volumeSlider.value)});showVolume(data.volume);adminResult.textContent=data.message}catch(error){adminResult.textContent=error.message}};
microSlider.oninput=()=>showMicro(microSlider.value);
microSlider.onchange=async()=>{try{const data=await adminPost("/admin/audio/microphone-sensitivity",{sensitivity:Number(microSlider.value)});applyPowerState(data);adminResult.textContent="Micro sensitivity saved"}catch(error){adminResult.textContent=error.message}};driveSpeedSlider.oninput=()=>showDriveSpeed(driveSpeedSlider.value);driveSpeedSlider.onchange=async()=>{try{const data=await adminPost("/admin/motors/speed",{speed:Number(driveSpeedSlider.value)});driveSpeedSlider.value=data.speed;showDriveSpeed(data.speed);adminResult.textContent=data.message}catch(error){adminResult.textContent=error.message}};cameraFpsSlider.oninput=()=>showCameraFps(cameraFpsSlider.value);cameraFpsSlider.onchange=()=>{const fps=setCameraFps(cameraFpsSlider.value);showCameraFps(fps);adminResult.textContent=`Camera refresh set to ${fps} fps`};
idleToggle.onclick=async()=>{try{
    const data=await adminPost("/admin/power/idle",{enabled:!runtimePower.idle_mode});applyPowerState(data);
    adminResult.textContent=data.idle_mode?"Idle mode enabled.":"Idle mode disabled.";
}catch(error){adminResult.textContent=error.message}};
for(const [name,button] of Object.entries(powerButtons))button.onclick=async()=>{try{const data=await adminPost("/admin/power/component",{component:name,enabled:!runtimePower[name]});applyPowerState(data)}catch(error){adminResult.textContent=error.message}};
localFeatureButtons.animation.button.onclick=()=>toggleLocalFeature("animation");
localFeatureButtons.sound.button.onclick=()=>toggleLocalFeature("sound");
document.querySelectorAll(".center-tab").forEach(tab=>tab.addEventListener("click",()=>{if(runtimePower.idle_mode)setTimeout(()=>{stopCameraRefresh();stopThermal()},0)}));

function setupWifiUI(){
    const row=document.querySelector(".wifi-row");if(!row)return;
    const nickname=document.createElement("input");nickname.id="wifi-nickname";nickname.placeholder="Wi-Fi nickname";row.prepend(nickname);
    const list=document.createElement("div");list.id="wifi-networks";list.className="wifi-networks";row.before(list);
    document.getElementById("wifi-add").onclick=addWifi;
}
async function addWifi(){
    const nickname=document.getElementById("wifi-nickname").value.trim(),ssid=document.getElementById("wifi-ssid").value.trim(),password=document.getElementById("wifi-password").value;
    if(!ssid||!password){adminResult.textContent="SSID and password are required";return}
    try{
        const data=await adminPost("/admin/wifi",{nickname,ssid,password});
        adminResult.textContent=data.message;document.getElementById("wifi-password").value="";
        await loadWifi();
    }catch(error){adminResult.textContent=`Wi-Fi: ${error.message}`;setTimeout(loadWifi,3000)}
}
function renderWifi(data){
    setWifiTransportName(data.current?.nickname||data.current?.ssid||"Offline");
    const list=document.getElementById("wifi-networks");if(!list)return;
    list.replaceChildren();const title=document.createElement("div");title.className="wifi-title";title.textContent="Known networks";list.appendChild(title);
    if(!data.networks?.length){const empty=document.createElement("div");empty.className="wifi-empty";empty.textContent="No saved Wi-Fi networks";list.appendChild(empty);return}
    for(const network of data.networks){
        const item=document.createElement("div");item.className=`wifi-network${network.active?" active":""}`;
        const info=document.createElement("div");info.className="wifi-network-info";const label=document.createElement("strong");label.textContent=network.nickname;const ssid=document.createElement("span");ssid.textContent=network.ssid;info.append(label,ssid);
        const actions=document.createElement("div");actions.className="wifi-network-actions";
        const connect=document.createElement("button");connect.textContent=network.active?"Connected":"Connect";connect.disabled=network.active;connect.onclick=async()=>{try{adminResult.textContent=(await adminPost("/admin/wifi/connect",{ssid:network.ssid})).message;setTimeout(loadWifi,2500)}catch(error){adminResult.textContent=error.message}};
        const remove=document.createElement("button");remove.textContent="Delete";remove.className="danger";remove.onclick=async()=>{if(!confirm(`Forget ${network.nickname}?`))return;try{adminResult.textContent=(await adminPost("/admin/wifi/delete",{ssid:network.ssid})).message;await loadWifi()}catch(error){adminResult.textContent=error.message}};
        actions.append(connect,remove);item.append(info,actions);list.appendChild(item);
    }
}
async function loadWifi(){try{renderWifi(await adminGet("/admin/wifi"))}catch(error){console.error("[WIFI]",error)}scheduleWifi()}
function scheduleWifi(){if(wifiTimer)clearTimeout(wifiTimer);wifiTimer=setTimeout(loadWifi,runtimePower.idle_mode?30000:15000)}

document.addEventListener("transportchange",async()=>{await Promise.allSettled([loadPower(),loadVolume(),loadDriveSpeed(),loadLedBrightness(),loadWifi()]);loadCameraFps()});
(async()=>{setupWifiUI();applyLocalFeature("animation");applyLocalFeature("sound");await Promise.allSettled([loadVolume(),loadPower(),loadDriveSpeed(),loadLedBrightness(),loadWifi()]);loadCameraFps()})();

// Face recognition and log display controls (Wi-Fi + BLE).
const faceEnabled=document.getElementById("face-enabled"),faceInterval=document.getElementById("face-interval-slider"),facePerformance=document.getElementById("face-performance");
async function refreshFaceStatus(){
    try{
        const data=transportMode==="bluetooth"?await bluetoothAdminRequest("vision_status"):await (async()=>{const response=await fetch("/vision/status",{cache:"no-store"});if(!response.ok)throw Error(`HTTP ${response.status}`);return response.json()})();faceEnabled.checked=!!data.enabled;faceInterval.value=String(data.interval||2);
        facePerformance.textContent=`Faces: ${data.faces?.length||0} · References: ${data.references||0} · Last: ${data.last_ms??"--"} ms · Avg: ${data.avg_ms??"--"} ms · Max: ${data.max_ms??"--"} ms · Errors: ${data.errors||0}${data.last_error?" · "+data.last_error:""}`;
    }catch(error){facePerformance.textContent=`Face status: ${error.message}`}
}
faceEnabled.onchange=async()=>{try{await adminPost("/vision/enable",{enabled:faceEnabled.checked});await refreshFaceStatus()}catch(error){adminResult.textContent=error.message;await refreshFaceStatus()}};
faceInterval.onchange=async()=>{try{await adminPost("/vision/interval",{interval:Number(faceInterval.value)});await refreshFaceStatus()}catch(error){adminResult.textContent=error.message}};
setInterval(()=>{if(document.getElementById("admin-view").classList.contains("active"))refreshFaceStatus()},2000);
refreshFaceStatus();

// Admin organized controls V2
const faceIntervalValue=document.getElementById("face-interval-value");
const logLevelChoices=[...document.querySelectorAll('input[name="log-level-choice"]')];
function syncLogChoices(){const level=localStorage.getItem("spy_log_level")||"INFO";logLevelChoices.forEach(input=>input.checked=input.value===level)}
function syncFaceInterval(){faceIntervalValue.textContent=`${faceInterval.value} s`;faceInterval.disabled=!faceEnabled.checked}
const previousFaceRefresh=refreshFaceStatus;
refreshFaceStatus=async function(){await previousFaceRefresh();syncFaceInterval()};
faceInterval.addEventListener("input",()=>{faceIntervalValue.textContent=`${faceInterval.value} s`});
faceInterval.addEventListener("change",syncFaceInterval);
faceEnabled.addEventListener("change",()=>setTimeout(syncFaceInterval,0));
logLevelChoices.forEach(input=>input.addEventListener("change",()=>{if(input.checked)localStorage.setItem("spy_log_level",input.value)}));
syncLogChoices();syncFaceInterval();
