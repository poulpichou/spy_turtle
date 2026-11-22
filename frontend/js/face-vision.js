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
const FRAME_KEY='spy_face_frame_style_v1';
const FRAME_STYLES={thin:'Thin rectangle',corners:'Corners only',circle:'Dotted circle',rect:'Green rectangle'};
function frameStyle(){const value=localStorage.getItem(FRAME_KEY)||'thin';return FRAME_STYLES[value]?value:'thin'}
function setFrameShape(shape,x,y,w,h){
 const style=frameStyle(),rect=shape.rect,ellipse=shape.ellipse||(shape.ellipse=document.createElementNS(NS,'ellipse')),corners=shape.corners||(shape.corners=document.createElementNS(NS,'path'));
 if(!ellipse.parentNode)shape.group.insertBefore(ellipse,shape.name);
 if(!corners.parentNode)shape.group.insertBefore(corners,shape.name);
 const thinPath=shape.thinPath||(shape.thinPath=document.createElementNS(NS,'path'));
 if(!thinPath.parentNode)shape.group.insertBefore(thinPath,shape.name);
 thinPath.setAttribute('d',`M${x} ${y}H${x+w}V${y+h}H${x}Z`);
 thinPath.setAttribute('fill','none');thinPath.setAttribute('stroke','#00ff66');
 thinPath.setAttribute('stroke-width','1');thinPath.setAttribute('vector-effect','non-scaling-stroke');
 thinPath.style.setProperty('stroke-width','1px','important');
 thinPath.style.display=style==='thin'?'':'none';
 for(const item of [rect,ellipse,corners]){item.setAttribute('fill','none');item.setAttribute('stroke','#00ff66');item.setAttribute('vector-effect','non-scaling-stroke');item.setAttribute('stroke-width',style==='rect'?'2':'1');item.style.setProperty('stroke-width',style==='rect'?'2px':'1px','important');item.setAttribute('stroke-dasharray','none')}
 rect.style.display=style==='rect'?'':'none';ellipse.style.display=style==='circle'?'':'none';corners.style.display=style==='corners'?'':'none';
 ellipse.setAttribute('cx',x+w/2);ellipse.setAttribute('cy',y+h/2);ellipse.setAttribute('rx',w*.845);ellipse.setAttribute('ry',h*.845);ellipse.setAttribute('stroke-dasharray','3 6');
 const a=Math.min(w,h)*.29;corners.setAttribute('d',`M${x+a} ${y}H${x}V${y+a} M${x+w-a} ${y}H${x+w}V${y+a} M${x} ${y+h-a}V${y+h}H${x+a} M${x+w-a} ${y+h}H${x+w}V${y+h-a}`);
}
function setupFrameAdmin(){
 if(document.getElementById('face-frame-style'))return;
 const target=document.getElementById('face-enabled')?.closest('.admin-section');if(!target)return;
 const line=document.createElement('div');line.className='admin-slider';const label=document.createElement('label');label.htmlFor='face-frame-style';label.textContent='Face detection frame (Turtle View OFF)';
 const picker=document.createElement('div');picker.className='spy-frame-picker';const button=document.createElement('button');button.type='button';button.id='face-frame-style';button.className='spy-frame-picker-button';button.setAttribute('aria-haspopup','listbox');button.setAttribute('aria-expanded','false');
 const menu=document.createElement('div');menu.className='spy-frame-picker-menu';menu.setAttribute('role','listbox');menu.hidden=true;
 function close(){menu.hidden=true;button.setAttribute('aria-expanded','false')}
 function refresh(){button.textContent=FRAME_STYLES[frameStyle()]+'  ▾';for(const option of menu.children){const selected=option.dataset.value===frameStyle();option.setAttribute('aria-selected',String(selected));option.classList.toggle('selected',selected)}}
 for(const [value,name] of Object.entries(FRAME_STYLES)){const option=document.createElement('button');option.type='button';option.className='spy-frame-picker-option';option.dataset.value=value;option.textContent=name;option.setAttribute('role','option');option.onclick=()=>{localStorage.setItem(FRAME_KEY,value);refresh();close();draw(lastFaces);drawThermal(lastFaces)};menu.append(option)}
 button.onclick=()=>{const opening=menu.hidden;menu.hidden=!opening;button.setAttribute('aria-expanded',String(opening))};button.onkeydown=e=>{if(e.key==='Escape')close()};menu.onkeydown=e=>{if(e.key==='Escape'){close();button.focus()}};
 document.addEventListener('pointerdown',e=>{if(!picker.contains(e.target))close()});picker.append(button,menu);refresh();line.append(label,picker);target.append(line);
}
const frameCss=document.createElement('style');frameCss.textContent=`.spy-frame-picker{position:relative;flex:0 1 46%;min-width:130px}.spy-frame-picker-button{width:100%;font:inherit;font-size:12px;text-align:left;padding:8px 10px;border:1px solid rgba(130,160,175,.4);border-radius:9px;background:#19272f;color:#f4f8fb;cursor:pointer}.spy-frame-picker-menu{position:absolute;right:0;top:calc(100% + 4px);min-width:100%;width:max-content;max-width:230px;z-index:9999;padding:4px;background:#19272f;border:1px solid rgba(130,160,175,.5);border-radius:10px;box-shadow:0 8px 24px #0008}.spy-frame-picker-menu[hidden]{display:none!important}.spy-frame-picker-option{display:block;width:100%;padding:9px 12px;border:0;border-radius:7px;background:transparent;color:#f4f8fb;font:inherit;font-size:12px;text-align:left;cursor:pointer}.spy-frame-picker-option.selected,.spy-frame-picker-option:hover{background:#34536a}.spy-frame-picker-option.selected:before{content:'✓ ';color:#91e8c7}`;document.head.append(frameCss);
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
        shape.rect.setAttribute("width",w);shape.rect.setAttribute("height",h);setFrameShape(shape,x,y,w,h);
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
setupFrameAdmin();setInterval(refresh,1000);
refresh();
})();