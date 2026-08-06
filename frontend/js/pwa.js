if("serviceWorker" in navigator){
    let reloading=false;
    navigator.serviceWorker.addEventListener("controllerchange",()=>{if(!reloading){reloading=true;location.reload()}});
    window.addEventListener("load",async()=>{try{const registration=await navigator.serviceWorker.register("/service-worker.js?v=8");await registration.update()}catch(error){console.error("[PWA]",error)}});
}
