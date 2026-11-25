/* V25: shared camera viewport for RGB/thermal detection overlays. */
(()=>{'use strict';
const view=document.getElementById('camera-view'),rgb=document.getElementById('camera-stream'),thermal=document.getElementById('thermal-stream');
if(!view||!rgb||!thermal)return;
const NS='http://www.w3.org/2000/svg',overlay=document.createElementNS(NS,'svg');overlay.id='face-overlay';overlay.setAttribute('aria-hidden','true');view.append(overlay);
let enabled=false,faces=[],seen=0,lastOk=0;const HOLD=3000,ALIGN={scaleX:1.25,scaleY:1,offsetX:0,offsetY:0};
const styles={thin:'Thin rectangle',corners:'Corners only',circle:'Dotted circle',rect:'Green rectangle'},KEY='spy_face_frame_style_v1';
const frameStyle=()=>styles[localStorage.getItem(KEY)]?localStorage.getItem(KEY):'thin';
function current(){return window.spyIsThermalVision?.()?thermal:rgb}
function geometry(){const img=current();if(!img.naturalWidth||!img.naturalHeight)return null;const b=img.getBoundingClientRect(),p=view.getBoundingClientRect(),r=Math.min(b.width/img.naturalWidth,b.height/img.naturalHeight),w=img.naturalWidth*r,h=img.naturalHeight*r;return {x:b.left-p.left+(b.width-w)/2,y:b.top-p.top+(b.height-h)/2,w,h}}
function normalized(f){let {x,y,w,h}=f;if(window.spyIsThermalVision?.()){x=(x-.5)*ALIGN.scaleX+.5+ALIGN.offsetX;y=(y-.5)*ALIGN.scaleY+.5+ALIGN.offsetY;w*=ALIGN.scaleX;h*=ALIGN.scaleY}return {x,y,w,h,name:f.name||'unknown'}}
function targets(){if(!enabled||Date.now()-seen>HOLD||!view.classList.contains('active'))return [];const g=geometry();if(!g)return [];return faces.map(f=>{const q=normalized(f);return {...q,px:g.x+(q.x+q.w/2)*g.w,py:g.y+(q.y+q.h/2)*g.h,width:q.w*g.w,height:q.h*g.h}}).filter(f=>f.width>0&&f.height>0&&f.px>=0&&f.py>=0&&f.px<=view.clientWidth&&f.py<=view.clientHeight)}
window.spyVisionTargets=targets;
function node(tag,attrs={},text){const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e}
function draw(){overlay.replaceChildren();if(!enabled||!view.classList.contains('active'))return;const g=geometry();if(!g)return;Object.assign(overlay.style,{position:'absolute',pointerEvents:'none',zIndex:'3',left:g.x+'px',top:g.y+'px',width:g.w+'px',height:g.h+'px'});overlay.setAttribute('viewBox',`0 0 ${g.w} ${g.h}`);
const style=frameStyle();for(const f of faces){const q=normalized(f),x=q.x*g.w,y=q.y*g.h,w=q.w*g.w,h=q.h*g.h;if(w<=0||h<=0)continue;const common={fill:'none',stroke:'#00ff66','stroke-width':style==='rect'?2:1,'vector-effect':'non-scaling-stroke'};
if(style==='circle')overlay.append(node('ellipse',{...common,cx:x+w/2,cy:y+h/2,rx:w*.845,ry:h*.845,'stroke-dasharray':'3 6'}));
else if(style==='corners'){const a=Math.min(w,h)*.29;overlay.append(node('path',{...common,d:`M${x+a} ${y}H${x}V${y+a} M${x+w-a} ${y}H${x+w}V${y+a} M${x} ${y+h-a}V${y+h}H${x+a} M${x+w-a} ${y+h}H${x+w}V${y+h-a}`}))}
else overlay.append(node('rect',{...common,x,y,width:w,height:h}));
overlay.append(node('text',{x:Math.max(2,x),y:Math.min(g.h-4,y+h+16),fill:'#00ff66','font-size':14,'font-weight':'bold','font-family':'Arial,sans-serif'},q.name));}}
async function poll(){try{const response=typeof transportMode!=='undefined'&&transportMode==='bluetooth'?await bluetoothAdminRequest('vision_status'):await fetch('/vision/status',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()});enabled=!!response.enabled;const incoming=Array.isArray(response.faces)?response.faces:[];lastOk=Date.now();if(incoming.length){faces=incoming;seen=lastOk}else if(!enabled||lastOk-seen>HOLD)faces=[]}catch(e){if(Date.now()-lastOk>5000){enabled=false;faces=[]}console.warn('[FACE]',e)}draw()}
function setupAdmin(){const section=document.getElementById('face-enabled')?.closest('.admin-section');if(!section||document.getElementById('face-frame-style'))return;const line=document.createElement('div');line.className='admin-slider';const label=document.createElement('label');label.htmlFor='face-frame-style';label.textContent='Face detection frame (Turtle View OFF)';const select=document.createElement('select');select.id='face-frame-style';for(const [key,value] of Object.entries(styles)){const option=document.createElement('option');option.value=key;option.textContent=value;select.append(option)}select.value=frameStyle();select.onchange=()=>{localStorage.setItem(KEY,select.value);draw()};line.append(label,select);section.append(line)}
setupAdmin();rgb.addEventListener('load',draw);thermal.addEventListener('load',draw);window.addEventListener('resize',draw);document.addEventListener('visibilitychange',()=>{if(!document.hidden)poll()});document.addEventListener('spyvisionchange',draw);setInterval(poll,1000);poll();
})();
