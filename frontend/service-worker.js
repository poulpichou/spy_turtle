const CACHE_NAME="spy-turtle-v2";
const APP_SHELL=[
    "/",
    "/index.html",
    "/css/style.css",
    "/css/mobile.css",
    "/js/api.js",
    "/js/dashboard.js",
    "/js/controls.js",
    "/js/camera.js",
    "/js/pwa.js",
    "/manifest.webmanifest",
    "/icons/turtle-192.png",
    "/icons/turtle-512.png",
    "/icons/turtle-maskable-512.png"
];

self.addEventListener("install",event=>{
    event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_SHELL)));
    self.skipWaiting();
});

self.addEventListener("activate",event=>{
    event.waitUntil(
        caches.keys()
            .then(keys=>Promise.all(keys.filter(key=>key!==CACHE_NAME).map(key=>caches.delete(key))))
            .then(()=>self.clients.claim())
    );
});

self.addEventListener("fetch",event=>{
    if(event.request.method!=="GET")return;
    const url=new URL(event.request.url);
    if(url.pathname.startsWith("/camera/")||url.pathname==="/state"||url.pathname==="/assets")return;
    event.respondWith(
        fetch(event.request)
            .then(response=>{
                const copy=response.clone();
                caches.open(CACHE_NAME).then(cache=>cache.put(event.request,copy));
                return response;
            })
            .catch(()=>caches.match(event.request))
    );
});
