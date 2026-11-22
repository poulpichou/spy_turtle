// Network-first frontend, offline fallback. The active cache is replaced only after successful install.
const CACHE="spy-turtle-ble-health-v1";
const APP_SHELL=["/","/index.html","/css/style.css?v=89","/css/mobile.css?v=28","/css/admin.css?v=16","/css/media.css?v=18","/css/joystick.css?v=1","/css/message-actions.css?v=27","/icons/turtle-192.png","/js/transport.js?v=20","/js/api.js?v=28","/js/dashboard.js?v=90","/js/controls.js?v=90","/js/joystick.js?v=10","/js/dropdowns.js?v=27","/js/camera.js?v=54","/js/bluetooth-vision.js?v=63","/js/center.js?v=23","/js/admin.js?v=20","/js/headlights.js?v=12","/js/voice.js?v=18","/js/message-layout.js?v=3","/js/pwa.js?v=34","/js/speech.js?v=31","/js/v21-features.js?v=29","/js/face-vision.js?v=62","/js/adaptive-volume.js?v=1","/js/v24.js?v=2","/js/sentinel.js?v=90","/js/v6-status.js?v=1","/js/automation.js?v=16","/js/automation-master.js?v=16","/js/commands.js?v=19"];
const isShell=url=>url.origin===self.location.origin&&(url.pathname==="/"||url.pathname==="/index.html"||url.pathname==="/manifest.webmanifest"||url.pathname.startsWith("/js/")||url.pathname.startsWith("/css/")||url.pathname.startsWith("/icons/"));
self.addEventListener("install",event=>event.waitUntil((async()=>{
    const cache=await caches.open(CACHE);
    try{await cache.addAll(APP_SHELL)}catch(error){await caches.delete(CACHE);throw error}
    await self.skipWaiting();
})()));
self.addEventListener("activate",event=>event.waitUntil((async()=>{
    await Promise.all((await caches.keys()).filter(name=>name.startsWith("spy-turtle-shell-")&&name!==CACHE).map(name=>caches.delete(name)));
    await self.clients.claim();
})()));
self.addEventListener("fetch",event=>{
    const request=event.request;if(request.method!=="GET"||!isShell(new URL(request.url)))return;
    event.respondWith((async()=>{
        const cache=await caches.open(CACHE);
        try{
            const response=await fetch(request,{cache:"no-store"});
            if(response.ok)await cache.put(request,response.clone());
            return response;
        }catch(error){
            const cached=await cache.match(request);if(cached)return cached;
            if(request.mode==="navigate"){
                const fallback=await cache.match("/index.html")||await cache.match("/");if(fallback)return fallback;
            }
            throw error;
        }
    })());
});
