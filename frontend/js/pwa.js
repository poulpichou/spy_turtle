// Offline-ready PWA; no persistent connectivity overlays. The existing transport button handles BLE.
const SPY_PWA_VERSION="clean-20261115";
window.addEventListener("load",async()=>{
    document.getElementById("bluetooth-offline-hint")?.remove();
    document.getElementById("remote-access-bar")?.remove();
    if(!("serviceWorker" in navigator))return;
    try{await navigator.serviceWorker.register(`/service-worker.js?v=${SPY_PWA_VERSION}`,{scope:"/"})}
    catch(error){console.warn("[PWA] Registration failed",error)}
});
