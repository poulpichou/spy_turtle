const CACHE="spy-turtle-shell-battery-debug-ui-20261113";
const APP_SHELL=["/", "/index.html", "/css/admin.css?v=15", "/css/joystick.css?v=1", "/css/media.css?v=17", "/css/message-actions.css?v=27", "/css/mobile.css?v=28", "/css/style.css?v=89", "/icons/turtle-192.png", "/js/adaptive-volume.js?v=1", "/js/admin.js?v=13", "/js/api.js?v=28", "/js/automation-master.js?v=16", "/js/automation.js?v=16", "/js/bluetooth-vision.js?v=61", "/js/camera.js?v=53", "/js/center.js?v=16", "/js/commands.js?v=17", "/js/controls.js?v=90", "/js/dashboard.js?v=90", "/js/dropdowns.js?v=27", "/js/face-vision.js?v=62", "/js/headlights.js?v=12", "/js/joystick.js?v=10", "/js/message-layout.js?v=3", "/js/pwa.js?v=28", "/js/sentinel.js?v=90", "/js/speech.js?v=28", "/js/transport.js?v=17", "/js/v21-features.js?v=28", "/js/v24.js?v=1", "/js/v6-status.js?v=1", "/js/voice.js?v=16", "/manifest.webmanifest?v=27"];
const isShell=url=>url.origin===self.location.origin&&(url.pathname==="/"||url.pathname==="/index.html"||url.pathname==="/manifest.webmanifest"||url.pathname.startsWith("/js/")||url.pathname.startsWith("/css/")||url.pathname.startsWith("/icons/"));
self.addEventListener("install",event=>event.waitUntil((async()=>{
    const cache=await caches.open(CACHE);
    await cache.addAll(APP_SHELL);
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
        try{const response=await fetch(request,{cache:"no-store"});if(response.ok)await cache.put(request,response.clone());return response}
        catch(error){const cached=await cache.match(request);if(cached)return cached;
            if(request.mode==="navigate"){const fallback=await cache.match("/index.html");if(fallback)return fallback}
            throw error;
        }
    })());
});
