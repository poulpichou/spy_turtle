const CACHE_NAME="spy-turtle-v3";
const STATIC_ASSETS=[
    "/manifest.webmanifest",
    "/icons/turtle-192.png",
    "/icons/turtle-512.png",
    "/icons/turtle-maskable-512.png"
];

self.addEventListener("install",event=>{
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache=>cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener("activate",event=>{
    event.waitUntil(
        caches.keys()
            .then(keys=>Promise.all(
                keys
                    .filter(key=>key!==CACHE_NAME)
                    .map(key=>caches.delete(key))
            ))
            .then(()=>self.clients.claim())
    );
});

self.addEventListener("fetch",event=>{
    if(event.request.method!=="GET")return;

    const url=new URL(event.request.url);

    if(
        url.pathname==="/"||
        url.pathname.endsWith(".html")||
        url.pathname.endsWith(".css")||
        url.pathname.endsWith(".js")||
        url.pathname.startsWith("/camera/")||
        url.pathname.startsWith("/photos")||
        url.pathname==="/logs"||
        url.pathname==="/state"||
        url.pathname==="/assets"
    ){
        event.respondWith(fetch(event.request,{cache:"no-store"}));
        return;
    }

    event.respondWith(
        caches.match(event.request).then(cached=>{
            if(cached)return cached;
            return fetch(event.request).then(response=>{
                const copy=response.clone();
                caches.open(CACHE_NAME).then(cache=>cache.put(event.request,copy));
                return response;
            });
        })
    );
});