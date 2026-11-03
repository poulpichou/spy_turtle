(()=>{
const image=document.getElementById("camera-stream");
const thermalImage=document.getElementById("thermal-stream");
const cameraView=document.getElementById("camera-view");
const thermalView=document.getElementById("thermal-view");
if(!image||!cameraView)return;
const NS="http://www.w3.org/2000/svg";
const overlay=document.createElementNS(NS,"svg");
overlay.id="face-overlay";
overlay.setAttribute("aria-hidden","true");
cameraView.appendChild(overlay);overlay.style.zIndex="3";
const thermalOverlay=document.createElementNS(NS,"svg");thermalOverlay.id="thermal-face-overlay";thermalOverlay.setAttribute("aria-hidden","true");thermalView.appendChild(thermalOverlay);thermalOverlay.style.zIndex="3";
let enabled=false;
let lastFaces=[];
let lastDetectedAt=0;
let lastSuccessfulPoll=0;
const HOLD_MS=3000;
const shapes=[];
const thermalShapes=[];
function clear(){for(const group of [shapes,thermalShapes]){group.forEach(pair=>pair.group.remove());group.length=0}}
function draw(faces){
    const visible=image;
    if(!enabled||!visible.naturalWidth||!visible.naturalHeight||!cameraView.classList.contains("active")){clear();return}
    const bounds=visible.getBoundingClientRect(),box=cameraView.getBoundingClientRect();
    const ratio=Math.min(bounds.width/visible.naturalWidth,bounds.height/visible.naturalHeight);
    const width=visible.naturalWidth*ratio,height=visible.naturalHeight*ratio;
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
// Thermal and RGB sensors share pointing direction but have different optics and mounting offsets.
// Adjust these normalized values after testing with a face at the center and near the edges.
const THERMAL_ALIGN={scaleX:1.25,scaleY:1,offsetX:0,offsetY:0,flipX:false,flipY:false}; // RGB center 80% maps to thermal width
function drawThermal(faces){
    if(!enabled||!thermalImage?.naturalWidth||!thermalImage.naturalHeight||!thermalView?.classList.contains("active")){thermalShapes.forEach(s=>s.group.remove());thermalShapes.length=0;return}
    const bounds=thermalImage.getBoundingClientRect(),box=thermalView.getBoundingClientRect();
    const ratio=Math.min(bounds.width/thermalImage.naturalWidth,bounds.height/thermalImage.naturalHeight);
    const width=thermalImage.naturalWidth*ratio,height=thermalImage.naturalHeight*ratio;
    thermalOverlay.style.position="absolute";thermalOverlay.style.pointerEvents="none";
    thermalOverlay.style.left=`${bounds.left-box.left+(bounds.width-width)/2}px`;
    thermalOverlay.style.top=`${bounds.top-box.top+(bounds.height-height)/2}px`;
    thermalOverlay.style.width=`${width}px`;thermalOverlay.style.height=`${height}px`;
    thermalOverlay.setAttribute("viewBox",`0 0 ${width} ${height}`);
    while(thermalShapes.length>faces.length)thermalShapes.pop().group.remove();
    for(let i=0;i<faces.length;i++){
        if(!thermalShapes[i]){const group=document.createElementNS(NS,"g"),rect=document.createElementNS(NS,"rect"),name=document.createElementNS(NS,"text");rect.setAttribute("fill","none");rect.setAttribute("stroke","#00ff66");rect.setAttribute("stroke-width","2");rect.setAttribute("vector-effect","non-scaling-stroke");name.setAttribute("fill","#00ff66");name.setAttribute("stroke","none");name.setAttribute("font-size","14");name.setAttribute("font-weight","bold");group.append(rect,name);thermalOverlay.appendChild(group);thermalShapes.push({group,rect,name})}
        const f=faces[i],shape=thermalShapes[i];
        let x=THERMAL_ALIGN.flipX?1-f.x-f.w:f.x,y=THERMAL_ALIGN.flipY?1-f.y-f.h:f.y;
        x=(x-.5)*THERMAL_ALIGN.scaleX+.5+THERMAL_ALIGN.offsetX;
        y=(y-.5)*THERMAL_ALIGN.scaleY+.5+THERMAL_ALIGN.offsetY;
        const w=f.w*THERMAL_ALIGN.scaleX,h=f.h*THERMAL_ALIGN.scaleY;
        shape.rect.setAttribute("x",x*width);shape.rect.setAttribute("y",y*height);
        shape.rect.setAttribute("width",w*width);shape.rect.setAttribute("height",h*height);
        shape.name.setAttribute("x",Math.max(2,x*width));shape.name.setAttribute("y",Math.min(height-4,(y+h)*height+16));shape.name.textContent=f.name||"unknown";
    }
}
async function refresh(){
    if(typeof transportMode!=="undefined"&&transportMode==="bluetooth"){
        // BLE observations are read through the existing admin characteristic.
    }
    try{
        const data=transportMode==="bluetooth"?await bluetoothAdminRequest("vision_status"):await (async()=>{const response=await fetch("/vision/status",{cache:"no-store"});if(!response.ok)throw Error(`HTTP ${response.status}`);return response.json()})();
        enabled=!!data.enabled;
        const incoming=Array.isArray(data.faces)?data.faces:[];
        const now=Date.now();lastSuccessfulPoll=now;
        if(incoming.length){lastFaces=incoming;lastDetectedAt=now}
        else if(!enabled||now-lastDetectedAt>HOLD_MS){lastFaces=[]}
        if(enabled){draw(lastFaces);drawThermal(lastFaces)}else{lastFaces=[];clear()}
    }catch(error){
        if(Date.now()-lastSuccessfulPoll>5000){lastFaces=[];clear()}
        console.warn("[FACE]",error);
    }
}
image.addEventListener("load",()=>draw(lastFaces));
thermalImage?.addEventListener("load",()=>drawThermal(lastFaces));
window.addEventListener("resize",()=>{draw(lastFaces);drawThermal(lastFaces)});
document.addEventListener("visibilitychange",()=>{if(document.hidden)clear();else refresh()});
setInterval(refresh,1000);
refresh();
})();