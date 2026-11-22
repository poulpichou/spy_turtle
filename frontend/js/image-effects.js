/* Spy Turtle Image Effects V9 - browser overlay, no extra packages or image assets. */
(()=>{
'use strict';
const image=document.getElementById('camera-stream'),view=document.getElementById('camera-view');if(!image||!view)return;
const MOODS={happy:'hearts',angry:'horns',curious:'question',excited:'stars',sad:'tear',sleepy:'zzz',sleeping:'zzz',proud:'none',playful:'animals',hungry:'salad',dizzy:'flip',robot:'robots',obedient:'robots',detective:'detective',dreamy:'dream',surprised:'surprise',shy:'none',rocket:'rocket',gassy:'gassy',sick:'sick'};
const KEY='spy_turtle_image_effects_v1',defaults={enabled:false};let config;try{config={...defaults,...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch(_){config={...defaults}}
delete config.manual;const save=()=>localStorage.setItem(KEY,JSON.stringify(config));
const VIEW_PREF_KEY='spy_turtle_view_preferences_v8';let viewPrefs;
try{viewPrefs={names:true,emojiScale:1,...JSON.parse(localStorage.getItem(VIEW_PREF_KEY)||'{}')}}catch(_){viewPrefs={names:true,emojiScale:1}}
if(!localStorage.getItem('spy_turtle_emoji_scale_v11_initialized')){viewPrefs.emojiScale=1;localStorage.setItem('spy_turtle_emoji_scale_v11_initialized','1');localStorage.setItem(VIEW_PREF_KEY,JSON.stringify(viewPrefs))}
viewPrefs.names=viewPrefs.names!==false;viewPrefs.emojiScale=Math.min(2,Math.max(.5,Number(viewPrefs.emojiScale)||1));
const saveViewPrefs=()=>localStorage.setItem(VIEW_PREF_KEY,JSON.stringify(viewPrefs));
const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg');svg.id='image-effects-overlay';svg.setAttribute('aria-hidden','true');Object.assign(svg.style,{position:'absolute',pointerEvents:'none',zIndex:'4',overflow:'hidden'});view.append(svg);
let mood='neutral',faces=[],lastFacesAt=0,enabledVision=false;const tracks=new Map();let nextId=1;let smokeSeed=0;
const element=(tag,attrs={},value)=>{const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(value!==undefined)e.textContent=value;return e};
function emoji(group,value,x,y,size,cls=''){const t=element('text',{x,y,'text-anchor':'middle','font-size':size,'dominant-baseline':'middle'},value);if(cls)t.setAttribute('class',cls);group.append(t);return t}
function effectName(){return config.enabled?(MOODS[mood]||'none'):'none'}
function assignTracks(incoming){const now=Date.now(),used=new Set();for(const f of incoming){const cx=f.x+f.w/2,cy=f.y+f.h/2;let best=null,bestDist=Infinity;for(const t of tracks.values()){if(used.has(t.id))continue;if(f.name&&f.name!=='unknown'&&t.name===f.name){best=t;break}const d=Math.hypot(cx-t.cx,cy-t.cy);if(d<bestDist&&d<Math.max(.12,f.w*.8)){best=t;bestDist=d}}if(!best){best={id:nextId++,animal:null,name:null,cx,cy,seen:now};tracks.set(best.id,best)}best.smoothX=best.smoothX===undefined?cx:best.smoothX*.84+cx*.16;best.smoothY=best.smoothY===undefined?cy:best.smoothY*.84+cy*.16;best.cx=cx;best.cy=cy;best.name=f.name&&f.name!=='unknown'?f.name:best.name;best.seen=now;used.add(best.id);f._track=best.id}for(const [id,t] of tracks)if(now-t.seen>12000)tracks.delete(id)}
function animalFor(id){const pool=['🐼','🦊','🐻','🐱','🐯','🐸','🐨','🐵','🦁','🐰'];const track=tracks.get(id);if(!track)return pool[0];if(track.animal)return track.animal;const used=new Set([...tracks.values()].map(t=>t.animal));track.animal=pool.find(a=>!used.has(a))||pool[(id-1)%pool.length];return track.animal}
function render(){
 svg.replaceChildren();const effect=effectName(),active=!!config.enabled;
 view.classList.toggle('image-effects-active',active);
 if(!active||!view.classList.contains('active')||!image.naturalWidth||!image.naturalHeight)return;
 if(effect!=='gassy'&&(!enabledVision||Date.now()-lastFacesAt>4500))return;
 const bounds=image.getBoundingClientRect(),parent=view.getBoundingClientRect(),ratio=Math.min(bounds.width/image.naturalWidth,bounds.height/image.naturalHeight),width=image.naturalWidth*ratio,height=image.naturalHeight*ratio;
 Object.assign(svg.style,{left:`${bounds.left-parent.left+(bounds.width-width)/2}px`,top:`${bounds.top-parent.top+(bounds.height-height)/2}px`,width:`${width}px`,height:`${height}px`});svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
 const catalog=window.spyVisionThoughts||{},people=catalog.people||{},moodCatalog=catalog.moods||{};
 const positions=faces.map(f=>({f,x:f.x*width,y:f.y*height,w:f.w*width,h:f.h*height}));
 const exclusive=new Set(['animals','salad','robots','flip','zzz','dream']);
 const mode=effect==='hearts'?'happy':effect==='horns'?'angry':effect==='question'?'curious':effect==='surprise'?'surprised':effect==='stars'?'excited':effect==='tear'?'sad':effect==='rocket'?'rocket':effect==='detective'?'detective':effect;
 const slot=Math.floor(Date.now()/10000);
 function sample(list,count,seed){const a=[...new Set(list||[])];for(let i=a.length-1;i>0;i--){seed=(seed*1664525+1013904223)>>>0;const j=seed%(i+1);[a[i],a[j]]=[a[j],a[i]]}return a.slice(0,count)}
 for(let i=0;i<positions.length;i++){
  const p=positions[i],{f,x,y,w,h}=p,cx=x+w/2,cy=y+h/2,size=Math.max(12,w),emojiBaseSize=Math.min(width*.28,Math.max(width*.14,size)),g=element('g');svg.append(g);
  const put=(value,px,py,scale,cls='spy-thought')=>emoji(g,value,px,py,scale,cls);
  if(viewPrefs.names&&f.name&&String(f.name).toLowerCase()!=='unknown'){
   const name=element('text',{x:Math.max(2,x),y:Math.min(height-4,y+h+16),fill:'#ffffff','font-size':14,'font-weight':'bold','font-family':'Arial, sans-serif','paint-order':'stroke',stroke:'#151515','stroke-width':2},String(f.name));g.append(name);
  }
  if(exclusive.has(effect)){
   if(effect==='animals')put(animalFor(f._track),cx,cy,size*1.2,'');
   else if(effect==='salad')put('🥗',cx,cy,size*1.25,'');
   else if(effect==='robots')put('🤖',cx,cy,size*1.2,'');
   else if(effect==='zzz'||effect==='dream')put((f._track||1)%2?'🐢':'🤖',cx,cy,size*1.25,'');
   else if(effect==='flip'&&positions.length===2){
    const other=positions[(i+1)%positions.length],ew=w*1.5,eh=h*1.5,ex=cx-ew/2,ey=cy-eh/2,ox=other.x+other.w/2,oy=other.y+other.h/2,id=`spy-swap-${i}`;
    const defs=element('defs'),clip=element('clipPath',{id});clip.append(element('rect',{x:ex,y:ey,width:ew,height:eh,rx:Math.max(2,ew*.07)}));defs.append(clip);g.append(defs);
    const clipped=element('g',{'clip-path':`url(#${id})`});clipped.append(element('image',{href:image.currentSrc||image.src,x:0,y:0,width,height,preserveAspectRatio:'none',transform:`translate(${cx-ox} ${cy-oy})`}));g.append(clipped);
   }
   continue;
  }
  if(effect==='horns')g.append(element('path',{d:`M ${x+w*.12} ${y+h*.04} Q ${x-w*.04} ${y-h*.43} ${x+w*.18} ${y-h*.49} Q ${x+w*.27} ${y-h*.24} ${x+w*.34} ${y+h*.01} Z M ${x+w*.66} ${y+h*.01} Q ${x+w*.73} ${y-h*.24} ${x+w*.82} ${y-h*.49} Q ${x+w*1.04} ${y-h*.43} ${x+w*.88} ${y+h*.04} Z`,fill:'#d62828',stroke:'#8c1010','stroke-width':Math.max(1,w*.018),'stroke-linejoin':'round'}));
  const key=String(f.name||'unknown').trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const matched=Object.keys(people).find(k=>k!=='unknown'&&(key===k||key.startsWith(k+' ')||key.endsWith(' '+k)));
  const personal=people[matched]||people.unknown||['🐢','🤖','❓'];const mood=moodCatalog[mode]||[];
  const seed=((f._track||i+1)*977+slot*37)>>>0;
  const moodCount=mood.length?Math.min(mood.length,slot%2?2:1):0;
  const personCount=moodCount?Math.min(personal.length,4-moodCount):Math.min(personal.length,3+(slot%2));
  const chosen=[...sample(personal,personCount,seed),...sample(mood,moodCount,seed+67)];
  const symbols=sample(chosen,Math.min(4,chosen.length),seed+91);
  const spots=[[-.40,-.54],[1.40,-.58],[.20,-.99],[.86,-1.00]];
  for(let j=0;j<symbols.length;j++){
   const [fx,fy]=spots[j],font=emojiBaseSize*(j<2?.29:.32)*3*.5*viewPrefs.emojiScale,margin=font*.7;
   const track=tracks.get(f._track),sx=track?(track.smoothX-f.x-f.w/2)*width:0,sy=track?(track.smoothY-f.y-f.h/2)*height:0;const px=Math.max(margin,Math.min(width-margin,x+w*fx+sx)),py=Math.max(margin,Math.min(height-margin,y+size*fy+sy));
   const e=put(symbols[j],px,py,font);e.style.animationDelay=`-${((Date.now()/1000)+(f._track||i+1)*7.3+j*11.7)%48}s`;
  }
 }
 if(effect==='gassy'&&!positions.length){const now=Date.now()/1000;for(let i=0;i<8;i++){const phase=(now*.19+i*.173)%1,x=(.08+((i*37)%83)/100)*width+Math.sin(now*.7+i*3)*width*.025,y=height*(1.12-phase*1.24),g=element('g',{opacity:(Math.sin(Math.PI*phase)*.65).toFixed(2)});svg.append(g);emoji(g,i%3===0?'☁️':'💨',x,y,Math.max(16,width*.035)*(1+phase*.65),'spy-thought')}}
}
async function poll(){try{const [v,state]=await Promise.all([transportMode==='bluetooth'?bluetoothAdminRequest('vision_status'):fetch('/vision/status',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}),transportMode==='bluetooth'?Promise.resolve(null):fetch('/state',{cache:'no-store'}).then(r=>r.ok?r.json():null)]);enabledVision=!!v.enabled;const incoming=Array.isArray(v.faces)?v.faces:[];if(incoming.length){faces=incoming.map(f=>({...f}));assignTracks(faces);lastFacesAt=Date.now()}else if(Date.now()-lastFacesAt>3000)faces=[];mood=state?.brain?.mood||mood}catch(e){if(Date.now()-lastFacesAt>4500)faces=[];console.debug('[IMAGE EFFECTS]',e.message)}render()}
function setupAdmin(){const recognition=document.getElementById('face-enabled')?.closest('.admin-face-heading');if(!recognition)return;document.getElementById('image-effects-section')?.remove();const section=document.createElement('section');section.className='admin-section';section.id='image-effects-section';const title=document.createElement('h3');title.textContent='Image Effects';section.append(title);const line=document.createElement('div');line.className='admin-face-heading';const label=document.createElement('label');label.htmlFor='image-effects-enabled';label.textContent='Activated (linked to mood)';const toggle=document.createElement('input');toggle.type='checkbox';toggle.id='image-effects-enabled';toggle.className='admin-switch';toggle.setAttribute('role','switch');toggle.checked=!!config.enabled;toggle.onchange=()=>{config.enabled=toggle.checked;save();render()};line.append(label,toggle);section.append(line);const namesLine=document.createElement('div');namesLine.className='admin-face-heading';const namesLabel=document.createElement('label');namesLabel.htmlFor='turtle-view-names';namesLabel.textContent="Display names in Turtle's View";const namesToggle=document.createElement('input');namesToggle.type='checkbox';namesToggle.id='turtle-view-names';namesToggle.className='admin-switch';namesToggle.setAttribute('role','switch');namesToggle.checked=viewPrefs.names;namesToggle.onchange=()=>{viewPrefs.names=namesToggle.checked;saveViewPrefs();render()};namesLine.append(namesLabel,namesToggle);section.append(namesLine);
 const sizeLine=document.createElement('div');sizeLine.className='admin-slider';const sizeLabel=document.createElement('label');sizeLabel.htmlFor='turtle-view-emoji-size';const sizeValue=document.createElement('span');sizeValue.id='turtle-view-emoji-size-value';sizeValue.textContent=`×${viewPrefs.emojiScale.toFixed(2)}`;const sizeSlider=document.createElement('input');sizeSlider.type='range';sizeSlider.id='turtle-view-emoji-size';sizeSlider.min='0.5';sizeSlider.max='2';sizeSlider.step='0.05';sizeSlider.value=String(viewPrefs.emojiScale);sizeLabel.textContent='Turtle View emoji size';sizeSlider.oninput=()=>{viewPrefs.emojiScale=Number(sizeSlider.value);sizeValue.textContent=`×${viewPrefs.emojiScale.toFixed(2)}`;saveViewPrefs();render()};sizeLine.classList.add('turtle-emoji-size-row');sizeLine.append(sizeLabel,sizeSlider,sizeValue);section.append(sizeLine);
recognition.closest('.admin-section')?.after(section)}
const css=document.createElement('style');css.textContent=`@keyframes spyThought{0%,100%{transform:translate(0px,0px) rotate(-1deg)}12.5%{transform:translate(10px,-8px) rotate(0deg)}25%{transform:translate(19px,-21px) rotate(1deg)}37.5%{transform:translate(13px,-34px) rotate(2deg)}50%{transform:translate(-4px,-38px) rotate(1deg)}62.5%{transform:translate(-19px,-27px) rotate(-1deg)}75%{transform:translate(-22px,-12px) rotate(-2deg)}87.5%{transform:translate(-12px,2px) rotate(-2deg)}}#image-effects-overlay .spy-thought{animation:spyThought 48s linear infinite;transform-box:fill-box;transform-origin:center}#camera-view.image-effects-active #face-overlay{display:none!important}@keyframes spyHeart{0%,100%{transform:translateY(5px)}50%{transform:translateY(-14px)}}@keyframes spyStar{0%,100%{transform:translate(-2px,2px) rotate(-8deg)}50%{transform:translate(3px,-7px) rotate(9deg)}}@keyframes spyFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}@keyframes spyBob{0%,100%{opacity:1}50%{opacity:.75}}@keyframes spyTwinkle{0%,100%{opacity:1}50%{opacity:.45}}@keyframes spyWander{0%,100%{transform:translate(0,0) rotate(-5deg)}25%{transform:translate(5px,-7px) rotate(7deg)}55%{transform:translate(-4px,-11px) rotate(-3deg)}80%{transform:translate(-6px,-3px) rotate(5deg)}}@keyframes spyWanderWide{0%,100%{transform:translate(0,5px) rotate(-7deg)}25%{transform:translate(12px,-13px) rotate(10deg)}55%{transform:translate(-10px,-23px) rotate(-6deg)}80%{transform:translate(-12px,-6px) rotate(8deg)}}#image-effects-overlay .spy-wander-wide{animation:spyWanderWide 5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}#image-effects-overlay .spy-wander{animation:spyWander 7.5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}#image-effects-overlay .spy-heart{animation:spyHeart 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}#image-effects-overlay .spy-star{animation:spyStar 3.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}#image-effects-overlay .spy-float{animation:spyFloat 2.4s ease-in-out infinite}#image-effects-overlay .spy-bob{animation:spyBob 1.6s ease-in-out infinite}#image-effects-overlay .spy-twinkle{animation:spyTwinkle 1.2s ease-in-out infinite}`;document.head.append(css);
setupAdmin();window.spyTurtleImageEffects={setEnabled(value){config.enabled=!!value;save();const t=document.getElementById('image-effects-enabled');if(t)t.checked=config.enabled;render()},isEnabled(){return !!config.enabled},render};image.addEventListener('load',render);window.addEventListener('resize',render);document.addEventListener('visibilitychange',render);setInterval(poll,1000);setInterval(()=>{if(effectName()==='gassy'&&view.classList.contains('active'))render()},220);poll();
})();
