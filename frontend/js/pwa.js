// PWA updates: check on launch and when returning online; keep Bluetooth-capable offline shell.
const SPY_PWA_VERSION="commands-sections-v1";
window.addEventListener("load",async()=>{
    document.getElementById("bluetooth-offline-hint")?.remove();
    document.getElementById("remote-access-bar")?.remove();
    if(!("serviceWorker" in navigator))return;
    let reloading=false;
    navigator.serviceWorker.addEventListener("controllerchange",()=>{
        if(reloading)return;
        reloading=true;window.location.reload();
    });
    try{
        const registration=await navigator.serviceWorker.register(`/service-worker.js?v=${SPY_PWA_VERSION}`,{scope:"/",updateViaCache:"none"});
        const check=()=>{if(navigator.onLine)registration.update().catch(error=>console.warn("[PWA] Update check failed",error))};
        window.addEventListener("online",check);
        document.addEventListener("visibilitychange",()=>{if(!document.hidden)check()});
        check();
    }catch(error){console.warn("[PWA] Registration failed",error)}
});
