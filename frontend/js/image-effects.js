/* Spy Turtle Image Effects V1 - browser-only overlay, no JPEG processing. */
(()=>{
'use strict';
const image=document.getElementById('camera-stream'),view=document.getElementById('camera-view');
if(!image||!view)return;
const EFFECTS={none:'None',hearts:'Happy · hearts',horns:'Angry · horns',question:'Curious · question mark',stars:'Excited · stars',tear:'Sad · tear',zzz:'Sleepy · Zzz',sparkles:'Proud · sparkles',animals:'Playful · animals',salad:'Hungry · salads',flip:'Dizzy · upside down'};
const MOODS={happy:'hearts',angry:'horns',curious:'question',excited:'stars',sad:'tear',sleepy:'zzz',sleeping:'zzz',proud:'sparkles',playful:'animals',hungry:'salad',dizzy:'flip'};
const KEY='spy_turtle_image_effects_v1',defaults={enabled:false,manual:'auto'};
let config;try{config={...defaults,...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch(_){config={...defaults}}
const save=()=>localStorage.setItem(KEY,JSON.stringify(config));
const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg');svg.id='image-effects-overlay';svg.setAttribute('aria-hidden','true');
Object.assign(svg.style,{position:'absolute',pointerEvents:'none',zIndex:'4',overflow:'visible'});view.append(svg);
let mood='neutral',faces=[],lastFacesAt=0,enabledVision=false;
const element=(tag,attrs={},value)=>{const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(value!==undefined)e.textContent=value;return e};
function emoji(group,value,x,y,size){group.append(element('text',{x,y,'text-anchor':'middle','font-size':size,'dominant-baseline':'middle'},value))}
function effectName(){return config.manual!=='auto'?config.manual:(config.enabled?(MOODS[mood]||'none'):'none')}
function render(){
 svg.replaceChildren();if(!view.classList.contains('active')||!image.naturalWidth||!image.naturalHeight)return;
 const effect=effectName();if(effect==='none'||!enabledVision||Date.now()-lastFacesAt>4500)return;
 const bounds=image.getBoundingClientRect(),parent=view.getBoundingClientRect(),ratio=Math.min(bounds.width/image.naturalWidth,bounds.height/image.naturalHeight);
 const width=image.naturalWidth*ratio,height=image.naturalHeight*ratio;
 Object.assign(svg.style,{left:`${bounds.left-parent.left+(bounds.width-width)/2}px`,top:`${bounds.top-parent.top+(bounds.height-height)/2}px`,width:`${width}px`,height:`${height}px`});svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
 for(const f of faces){const x=f.x*width,y=f.y*height,w=f.w*width,h=f.h*height,cx=x+w/2,cy=y+h/2,s=Math.max(12,w);
  const g=element('g');svg.append(g);
  if(effect==='hearts'){emoji(g,'💕',x+w*.2,y-s*.14,s*.40);emoji(g,'💗',x+w*.85,y-s*.12,s*.28)}
  else if(effect==='horns'){emoji(g,'😈',cx,y-s*.16,s*.68)}
  else if(effect==='question')emoji(g,'❓',x+w*.85,y-s*.2,s*.45);
  else if(effect==='stars'){emoji(g,'✨',x+w*.1,y-s*.12,s*.40);emoji(g,'⭐',x+w*.9,y-s*.15,s*.32)}
  else if(effect==='tear')emoji(g,'💧',x+w*.22,y+h*.65,s*.26);
  else if(effect==='zzz')emoji(g,'💤',x+w*.9,y-s*.12,s*.45);
  else if(effect==='sparkles')emoji(g,'✨',cx,y-s*.15,s*.5);
  else if(effect==='animals')emoji(g,['🐼','🦊','🐻','🐱'][Math.floor((cx+cy)%4)],cx,cy,s*1.2);
  else if(effect==='salad')emoji(g,'🥗',cx,cy,s*1.25);
  else if(effect==='flip'){const t=element('g',{transform:`rotate(180 ${cx} ${cy})`});g.append(t);emoji(t,'🙃',cx,cy,s*1.05)}
 }
}
async function poll(){
 try{const [v,state]=await Promise.all([transportMode==='bluetooth'?bluetoothAdminRequest('vision_status'):fetch('/vision/status',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}),transportMode==='bluetooth'?Promise.resolve(null):fetch('/state',{cache:'no-store'}).then(r=>r.ok?r.json():null)]);
 enabledVision=!!v.enabled;faces=Array.isArray(v.faces)?v.faces:[];if(faces.length)lastFacesAt=Date.now();else if(Date.now()-lastFacesAt>3000)faces=[];
 mood=state?.brain?.mood||mood;
 }catch(e){if(Date.now()-lastFacesAt>4500)faces=[];console.debug('[IMAGE EFFECTS]',e.message)}render();
}
function setupAdmin(){
 const recognition=document.getElementById('face-enabled')?.closest('.admin-face-heading');if(!recognition)return;
 const section=document.createElement('section');section.className='admin-section';section.id='image-effects-section';
 const title=document.createElement('h3');title.textContent='Image Effects';section.append(title);
 const line=document.createElement('div');line.className='admin-face-heading';
 const label=document.createElement('label');label.htmlFor='image-effects-enabled';label.textContent='Activated (linked to mood)';
 const toggle=document.createElement('input');toggle.type='checkbox';toggle.id='image-effects-enabled';toggle.className='admin-switch';toggle.setAttribute('role','switch');toggle.checked=!!config.enabled;
 toggle.onchange=()=>{config.enabled=toggle.checked;save();render()};line.append(label,toggle);section.append(line);
 const manualLine=document.createElement('div');manualLine.className='admin-slider';const manualLabel=document.createElement('label');manualLabel.htmlFor='image-effects-manual';manualLabel.textContent='Immediate modifier (priority)';
 const select=document.createElement('select');select.id='image-effects-manual';select.style.width='100%';for(const [value,name] of Object.entries({auto:'Auto (follow mood)',...EFFECTS})){const option=document.createElement('option');option.value=value;option.textContent=name;select.append(option)}select.value=config.manual;
 select.onchange=()=>{config.manual=select.value;save();render()};manualLine.append(manualLabel,select);section.append(manualLine);
 recognition.closest('.admin-section')?.after(section);
}
setupAdmin();image.addEventListener('load',render);window.addEventListener('resize',render);document.addEventListener('visibilitychange',render);setInterval(poll,1000);poll();
})();
