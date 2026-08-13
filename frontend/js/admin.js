const adminResult=document.getElementById("admin-result");
const volumeSlider=document.getElementById("volume-slider"),volumeValue=document.getElementById("volume-value");
const microSlider=document.getElementById("micro-slider"),microValue=document.getElementById("micro-value");
const idleToggle=document.getElementById("idle-toggle");
const powerButtons={back_screen:document.getElementById("back-screen-toggle"),eyes:document.getElementById("eyes-toggle"),shell_light:document.getElementById("shell-light-toggle")};
const localFeatureButtons={animation:{button:document.getElementById("animation-toggle"),select:"animation-select",card:".animation-card",storage:"spy_turtle_animation_enabled"},sound:{button:document.getElementById("sound-toggle"),select:"sound-select",card:".sound-card",storage:"spy_turtle_sound_enabled"}};
const idleDirectionalIds=["forward","backward","left","right","stop","head-up","head-down","head-left","head-right","head-center"];
const idleControlIds=["face-select","shell-select","led-select","photo-button","listen-button","record-message","screen-message-button"];
let runtimePower={idle_mode:false,back_screen:true,eyes:true,shell_light:true,microphone_sensitivity:60};
let localFeatures={animation:localStorage.getItem(localFeatureButtons.animation.storage)!=="false",sound:localStorage.getItem(localFeatureButtons.sound.storage)!=="false"};
let wifiTimer=null;

async function adminPost(path,body){
    const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):null});
    const text=await response.text(),data=text?JSON.parse(text):{ok:response.ok,message:"Command sent"};
    if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);
    return data;
}
function showVolume(value){volumeValue.textContent=`${value}%`}
function showMicro(value){microValue.textContent=`${value}%`}
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
function applyPowerState(state){
    runtimePower={...runtimePower,...state};
    idleToggle.classList.toggle("active",runtimePower.idle_mode);
    idleToggle.querySelector("span").textContent=runtimePower.idle_mode?"Idle mode ON":"Idle mode";
    for(const [name,button] of Object.entries(powerButtons)){
        button.classList.toggle("active",!!runtimePower[name]);
        button.classList.toggle("off",!runtimePower[name]);
        button.disabled=runtimePower.idle_mode;
        button.closest(".right-control")?.classList.toggle("idle-disabled",runtimePower.idle_mode);
    }
    idleDirectionalIds.forEach(id=>{const button=document.getElementById(id);if(button)button.disabled=runtimePower.idle_mode});
    idleControlIds.forEach(id=>{
        const element=document.getElementById(id);if(!element)return;
        if(element.tagName==="SELECT")setSelectDisabled(id,runtimePower.idle_mode);
        else element.disabled=runtimePower.idle_mode;
    });
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
async function loadPower(){try{const response=await fetch("/admin/power",{cache:"no-store"});if(response.ok)applyPowerState(await response.json())}catch(error){console.error("[POWER]",error)}}

document.querySelectorAll("[data-admin-action]").forEach(button=>button.onclick=async()=>{
    const action=button.dataset.adminAction,labels={restart:"restart Spy Turtle",reboot:"reboot the Raspberry Pi",shutdown:"shut down the Raspberry Pi"};
    if(!confirm(`Really ${labels[action]}?`))return;
    try{adminResult.textContent=(await adminPost(action==="restart"?"/admin/turtle/restart":`/admin/system/${action}`)).message}
    catch(error){adminResult.textContent=["restart","reboot","shutdown"].includes(action)?"Command sent":error.message}
});
volumeSlider.oninput=()=>showVolume(volumeSlider.value);
volumeSlider.onchange=async()=>{try{const data=await adminPost("/admin/audio/volume",{volume:Number(volumeSlider.value)});showVolume(data.volume);adminResult.textContent=data.message}catch(error){adminResult.textContent=error.message}};
microSlider.oninput=()=>showMicro(microSlider.value);
microSlider.onchange=async()=>{try{const data=await adminPost("/admin/audio/microphone-sensitivity",{sensitivity:Number(microSlider.value)});applyPowerState(data);adminResult.textContent="Micro sensitivity saved (display only until microphone is installed)"}catch(error){adminResult.textContent=error.message}};
idleToggle.onclick=async()=>{try{
    const data=await adminPost("/admin/power/idle",{enabled:!runtimePower.idle_mode});applyPowerState(data);
    const governors=Object.values(data.cpu_governors||{}),cpu=data.idle_mode?(governors.length?` CPU: ${[...new Set(governors)].join("/")}.`:""):"";
    adminResult.textContent=data.idle_mode?`Idle mode enabled.${cpu}`:"Idle mode disabled — normal CPU governor restored.";
}catch(error){adminResult.textContent=error.message}};
for(const [name,button] of Object.entries(powerButtons))button.onclick=async()=>{try{const data=await adminPost("/admin/power/component",{component:name,enabled:!runtimePower[name]});applyPowerState(data)}catch(error){adminResult.textContent=error.message}};
localFeatureButtons.animation.button.onclick=()=>toggleLocalFeature("animation");
localFeatureButtons.sound.button.onclick=()=>toggleLocalFeature("sound");
document.querySelectorAll(".center-tab").forEach(tab=>tab.addEventListener("click",()=>{if(runtimePower.idle_mode)setTimeout(()=>{stopCameraRefresh();stopThermal()},0)}));

function setupWifiUI(){
    const row=document.querySelector(".wifi-row");if(!row)return;
    const nickname=document.createElement("input");nickname.id="wifi-nickname";nickname.placeholder="Wi-Fi nickname";row.prepend(nickname);
    const list=document.createElement("div");list.id="wifi-networks";list.className="wifi-networks";row.before(list);
    const statusBar=document.getElementById("status-bar");
    if(statusBar&&!document.getElementById("wifi-name")){const item=document.createElement("div");item.className="wifi-status";item.innerHTML='📶 <span id="wifi-name">--</span>';statusBar.appendChild(item)}
    document.getElementById("wifi-add").onclick=addWifi;
}
async function addWifi(){
    const nickname=document.getElementById("wifi-nickname").value.trim(),ssid=document.getElementById("wifi-ssid").value.trim(),password=document.getElementById("wifi-password").value;
    if(!ssid||!password){adminResult.textContent="SSID and password are required";return}
    try{const data=await adminPost("/admin/wifi",{nickname,ssid,password});adminResult.textContent=data.message;document.getElementById("wifi-password").value="";await loadWifi()}
    catch(error){adminResult.textContent=`Wi-Fi command sent or connection changed: ${error.message}`;setTimeout(loadWifi,3000)}
}
function renderWifi(data){
    const list=document.getElementById("wifi-networks"),name=document.getElementById("wifi-name");if(name)name.textContent=data.current?.nickname||data.current?.ssid||"Offline";if(!list)return;
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
async function loadWifi(){try{const response=await fetch("/admin/wifi",{cache:"no-store"});if(response.ok)renderWifi(await response.json())}catch(error){console.error("[WIFI]",error)}scheduleWifi()}
function scheduleWifi(){if(wifiTimer)clearTimeout(wifiTimer);wifiTimer=setTimeout(loadWifi,runtimePower.idle_mode?30000:15000)}

(async()=>{setupWifiUI();applyLocalFeature("animation");applyLocalFeature("sound");try{const response=await fetch("/admin/audio/volume",{cache:"no-store"});if(response.ok){const data=await response.json();volumeSlider.value=data.volume;showVolume(data.volume)}}catch(error){console.error("[VOLUME]",error)}await loadPower();await loadWifi()})();
