const adminResult=document.getElementById("admin-result");
const volumeSlider=document.getElementById("volume-slider"),volumeValue=document.getElementById("volume-value");
const microSlider=document.getElementById("micro-slider"),microValue=document.getElementById("micro-value");
const idleToggle=document.getElementById("idle-toggle");
const powerButtons={back_screen:document.getElementById("back-screen-toggle"),eyes:document.getElementById("eyes-toggle"),shell_light:document.getElementById("shell-light-toggle")};
let runtimePower={idle_mode:false,back_screen:true,eyes:true,shell_light:true,microphone_sensitivity:60};

async function adminPost(path,body){
    const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):null});
    const text=await response.text(),data=text?JSON.parse(text):{ok:response.ok,message:"Command sent"};
    if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);
    return data;
}
function showVolume(value){volumeValue.textContent=`${value}%`}
function showMicro(value){microValue.textContent=`${value}%`}
function applyPowerState(state){
    runtimePower={...runtimePower,...state};
    idleToggle.classList.toggle("active",runtimePower.idle_mode);
    idleToggle.textContent=runtimePower.idle_mode?"Idle mode ON":"Idle mode";
    for(const [name,button] of Object.entries(powerButtons)){
        button.classList.toggle("active",!!runtimePower[name]);
        button.classList.toggle("off",!runtimePower[name]);
        button.disabled=runtimePower.idle_mode;
    }
    microSlider.value=runtimePower.microphone_sensitivity??60;showMicro(microSlider.value);
    if(runtimePower.idle_mode){stopCameraRefresh();stopThermal()}
    else if(typeof activeView!=="undefined"){
        if(activeView==="camera")startCameraRefresh();
        else if(activeView==="thermal"&&!thermalTimer)startThermal();
    }
}
async function loadPower(){
    try{
        const response=await fetch("/admin/power",{cache:"no-store"});
        if(response.ok)applyPowerState(await response.json());
    }catch(error){console.error("[POWER]",error)}
}

document.querySelectorAll("[data-admin-action]").forEach(button=>button.onclick=async()=>{
    const action=button.dataset.adminAction,labels={restart:"restart Spy Turtle",reboot:"reboot the Raspberry Pi",shutdown:"shut down the Raspberry Pi"};
    if(!confirm(`Really ${labels[action]}?`))return;
    try{adminResult.textContent=(await adminPost(action==="restart"?"/admin/turtle/restart":`/admin/system/${action}`)).message}
    catch(error){adminResult.textContent=["restart","reboot","shutdown"].includes(action)?"Command sent":error.message}
});
document.getElementById("wifi-add").onclick=async()=>{
    const ssid=document.getElementById("wifi-ssid").value.trim(),password=document.getElementById("wifi-password").value;
    if(!ssid||!password){adminResult.textContent="SSID and password are required";return}
    try{adminResult.textContent=(await adminPost("/admin/wifi",{ssid,password})).message;document.getElementById("wifi-password").value=""}
    catch(error){adminResult.textContent=error.message}
};
volumeSlider.oninput=()=>showVolume(volumeSlider.value);
volumeSlider.onchange=async()=>{
    try{const data=await adminPost("/admin/audio/volume",{volume:Number(volumeSlider.value)});showVolume(data.volume);adminResult.textContent=data.message}
    catch(error){adminResult.textContent=error.message}
};
microSlider.oninput=()=>showMicro(microSlider.value);
microSlider.onchange=async()=>{
    try{const data=await adminPost("/admin/audio/microphone-sensitivity",{sensitivity:Number(microSlider.value)});applyPowerState(data);adminResult.textContent="Micro sensitivity saved (display only until microphone is installed)"}
    catch(error){adminResult.textContent=error.message}
};
idleToggle.onclick=async()=>{
    try{const data=await adminPost("/admin/power/idle",{enabled:!runtimePower.idle_mode});applyPowerState(data);adminResult.textContent=data.idle_mode?"Idle mode enabled — cameras and background visual loops paused":"Idle mode disabled"}
    catch(error){adminResult.textContent=error.message}
};
for(const [name,button] of Object.entries(powerButtons))button.onclick=async()=>{
    try{const data=await adminPost("/admin/power/component",{component:name,enabled:!runtimePower[name]});applyPowerState(data)}
    catch(error){adminResult.textContent=error.message}
};
document.querySelectorAll(".center-tab").forEach(tab=>tab.addEventListener("click",()=>{if(runtimePower.idle_mode)setTimeout(()=>{stopCameraRefresh();stopThermal()},0)}));
(async()=>{
    try{
        const response=await fetch("/admin/audio/volume",{cache:"no-store"});
        if(response.ok){const data=await response.json();volumeSlider.value=data.volume;showVolume(data.volume)}
    }catch(error){console.error("[VOLUME]",error)}
    await loadPower();
})();
