// Offline-ready PWA: preserve the app shell and leave API responses uncached.
const SPY_PWA_VERSION="remote-20261113";
async function registerFrontendCache(){
    if(!("serviceWorker" in navigator))return;
    try{
        const registration=await navigator.serviceWorker.register(`/service-worker.js?v=${SPY_PWA_VERSION}`,{scope:"/"});
        await navigator.serviceWorker.ready;
        console.info("[PWA] Offline app shell ready",registration.scope);
    }catch(error){console.warn("[PWA] Offline installation failed",error)}
}
function showBluetoothOfflineHint(){
    if(document.getElementById("bluetooth-offline-hint"))return;
    const hint=document.createElement("div");hint.id="bluetooth-offline-hint";
    hint.style.cssText="position:fixed;bottom:12px;left:50%;transform:translateX(-50%);z-index:9999;background:#202832;color:white;padding:10px 14px;border:1px solid #657586;border-radius:10px;max-width:90vw;box-shadow:0 4px 18px #0008;font:13px sans-serif;display:flex;gap:10px;align-items:center";
    const text=document.createElement("span");text.textContent="No Wi-Fi? Connect directly to Spy Turtle over Bluetooth.";
    const button=document.createElement("button");button.type="button";button.textContent="Connect Bluetooth";button.style.cssText="padding:8px;border-radius:7px;white-space:nowrap";
    button.onclick=async()=>{button.disabled=true;try{if(transportMode!=="bluetooth")await connectBluetooth();hint.remove()}catch(error){alert(`Bluetooth: ${error.message}`)}finally{button.disabled=false}};
    hint.append(text,button);document.body.appendChild(hint);
}
window.addEventListener("load",()=>{
    registerFrontendCache();
    if(typeof transportMode!=="undefined"&&transportMode!=="bluetooth"){if(!navigator.onLine)showBluetoothOfflineHint();probeRobotWifi()}
});
window.addEventListener("offline",()=>{if(transportMode!=="bluetooth")showBluetoothOfflineHint()});
window.addEventListener("online",()=>document.getElementById("bluetooth-offline-hint")?.remove());
document.addEventListener("transportchange",()=>{if(transportMode==="bluetooth")document.getElementById("bluetooth-offline-hint")?.remove()});

async function probeRobotWifi(){
    if(typeof transportMode==="undefined"||transportMode==="bluetooth")return;
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),2500);
    try{
        const response=await fetch("/state",{cache:"no-store",signal:controller.signal});
        if(!response.ok)throw Error("Robot unreachable");
        document.getElementById("bluetooth-offline-hint")?.remove();
    }catch(error){if(transportMode!=="bluetooth")showBluetoothOfflineHint()}
    finally{clearTimeout(timer)}
}
document.addEventListener("visibilitychange",()=>{if(!document.hidden)probeRobotWifi()});
