(()=>{
const image=document.getElementById("camera-stream");
const cameraView=document.getElementById("camera-view");
if(!image||!cameraView)return;
const NS="http://www.w3.org/2000/svg";
const overlay=document.createElementNS(NS,"svg");
overlay.id="face-overlay";
overlay.setAttribute("aria-hidden","true");
cameraView.appendChild(overlay);
let enabled=false;
let lastFaces=[];
let lastSuccessfulPoll=0;
function clear(){overlay.replaceChildren()}
function draw(faces){
    clear();
    if(!enabled||!image.naturalWidth||!image.naturalHeight||!cameraView.classList.contains("active"))return;
    const bounds=image.getBoundingClientRect(),box=cameraView.getBoundingClientRect();
    const ratio=Math.min(bounds.width/image.naturalWidth,bounds.height/image.naturalHeight);
    const width=image.naturalWidth*ratio,height=image.naturalHeight*ratio;
    overlay.style.left=`${bounds.left-box.left+(bounds.width-width)/2}px`;
    overlay.style.top=`${bounds.top-box.top+(bounds.height-height)/2}px`;
    overlay.style.width=`${width}px`;
    overlay.style.height=`${height}px`;
    overlay.setAttribute("viewBox",`0 0 ${width} ${height}`);
    for(const face of faces){
        const x=face.x*width,y=face.y*height,w=face.w*width,h=face.h*height;
        const rect=document.createElementNS(NS,"rect");
        rect.setAttribute("x",x);rect.setAttribute("y",y);
        rect.setAttribute("width",w);rect.setAttribute("height",h);
        overlay.appendChild(rect);
        const name=document.createElementNS(NS,"text");
        name.setAttribute("x",Math.max(2,x));
        name.setAttribute("y",Math.min(height-4,y+h+16));
        name.textContent=face.name||"unknown";
        overlay.appendChild(name);
    }
}
async function refresh(){
    if(typeof transportMode!=="undefined"&&transportMode==="bluetooth"){
        enabled=false;lastFaces=[];clear();return;
    }
    try{
        const response=await fetch("/vision/status",{cache:"no-store"});
        if(!response.ok)throw Error(`HTTP ${response.status}`);
        const data=await response.json();
        enabled=!!data.enabled;
        lastFaces=Array.isArray(data.faces)?data.faces:[];
        lastSuccessfulPoll=Date.now();
        if(enabled)draw(lastFaces);else clear();
    }catch(error){
        if(Date.now()-lastSuccessfulPoll>5000){lastFaces=[];clear()}
        console.warn("[FACE]",error);
    }
}
image.addEventListener("load",()=>draw(lastFaces));
window.addEventListener("resize",()=>draw(lastFaces));
document.addEventListener("visibilitychange",()=>{if(document.hidden)clear();else refresh()});
setInterval(refresh,1000);
refresh();
})();