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
let lastDetectedAt=0;
let lastSuccessfulPoll=0;
const HOLD_MS=3000;
const shapes=[];
function clear(){shapes.forEach(pair=>pair.group.remove());shapes.length=0}
function draw(faces){
    if(!enabled||!image.naturalWidth||!image.naturalHeight||!cameraView.classList.contains("active")){clear();return}
    const bounds=image.getBoundingClientRect(),box=cameraView.getBoundingClientRect();
    const ratio=Math.min(bounds.width/image.naturalWidth,bounds.height/image.naturalHeight);
    const width=image.naturalWidth*ratio,height=image.naturalHeight*ratio;
    overlay.style.left=`${bounds.left-box.left+(bounds.width-width)/2}px`;
    overlay.style.top=`${bounds.top-box.top+(bounds.height-height)/2}px`;
    overlay.style.width=`${width}px`;
    overlay.style.height=`${height}px`;
    overlay.setAttribute("viewBox",`0 0 ${width} ${height}`);
    while(shapes.length>faces.length){shapes.pop().group.remove()}
    for(let i=0;i<faces.length;i++){
        if(!shapes[i]){
            const group=document.createElementNS(NS,"g"),rect=document.createElementNS(NS,"rect"),name=document.createElementNS(NS,"text");
            group.append(rect,name);overlay.appendChild(group);shapes.push({group,rect,name});
        }
        const face=faces[i],shape=shapes[i],x=face.x*width,y=face.y*height,w=face.w*width,h=face.h*height;
        shape.rect.setAttribute("x",x);shape.rect.setAttribute("y",y);
        shape.rect.setAttribute("width",w);shape.rect.setAttribute("height",h);
        shape.name.setAttribute("x",Math.max(2,x));
        shape.name.setAttribute("y",Math.min(height-4,y+h+16));
        shape.name.textContent=face.name||"unknown";
    }
}
async function refresh(){
    if(typeof transportMode!=="undefined"&&transportMode==="bluetooth"){
        enabled=false;lastFaces=[];lastDetectedAt=0;clear();return;
    }
    try{
        const response=await fetch("/vision/status",{cache:"no-store"});
        if(!response.ok)throw Error(`HTTP ${response.status}`);
        const data=await response.json();
        enabled=!!data.enabled;
        const incoming=Array.isArray(data.faces)?data.faces:[];
        const now=Date.now();lastSuccessfulPoll=now;
        if(incoming.length){lastFaces=incoming;lastDetectedAt=now}
        else if(!enabled||now-lastDetectedAt>HOLD_MS){lastFaces=[]}
        if(enabled)draw(lastFaces);else{lastFaces=[];clear()}
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