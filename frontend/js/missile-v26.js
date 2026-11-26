/* V26: mode-aware playful camera projectiles; visual only, never controls hardware. */
(()=>{'use strict';
const view=document.getElementById('camera-view'),button=document.getElementById('head-missile');if(!view||!button)return;
const stage=document.createElement('div');stage.className='spy-missile-stage spy-weapon-stage';stage.setAttribute('aria-hidden','true');view.append(stage);
const vegetables=[['🥕','#f58a27'],['🥦','#4d9b37'],['🥬','#7fc957'],['🥒','#71a83c'],['🌶️','#e33a32'],['🫑','#50a83e'],['🌽','#efc849'],['🍆','#783ca1'],['🥔','#b99466'],['🧅','#d6b88a'],['🧄','#e6e0ce'],['🍅','#ec4136'],['🫛','#68ad49'],['🍄','#d94b40']];
const produce=[...vegetables,...[['🍌','#f4d343'],['🍎','#d62d30'],['🍏','#87c43b'],['🍐','#a6c43b'],['🍊','#ff962b'],['🍋','#f5d948'],['🍋‍🟩','#91bd43'],['🍉','#e94d60'],['🍇','#8151b3'],['🍓','#e93448'],['🫐','#5363ba'],['🍒','#c82a42'],['🍑','#f39a74'],['🥭','#f3a832'],['🍍','#e9c33d'],['🥥','#c7b18f'],['🥝','#8fba48'],['🍈','#b4d479']]];
let busy=false;const mode=()=>{const m=localStorage.getItem('spy_grid_vision_mode');return m==='turtle'||m==='thermal'?m:'robot'};
function sync(){const m=mode();button.textContent=m==='turtle'?'🍌':m==='thermal'?'🔫':'🚀';button.title=m==='turtle'?'Launch a random fruit or vegetable':m==='thermal'?'Fire thermal laser':'Launch missile';button.setAttribute('aria-label',button.title)}
sync();document.addEventListener('click',e=>{if(e.target.closest?.('.spy-vision-segment'))queueMicrotask(sync)});window.addEventListener('storage',sync);
const put=(cls,text,x,y)=>{const e=document.createElement('div');e.className=cls;e.textContent=text;e.style.left=x+'px';e.style.top=y+'px';stage.append(e);return e};
const move=(e,x,y,deg=0)=>{e.style.left=x+'px';e.style.top=y+'px';e.style.transform=`translate(-50%,-50%) rotate(${deg}deg)`};
const bez=(a,b,c,t)=>{const u=1-t;return u*u*a+2*u*t*b+t*t*c};
const curve=(a,b,c,d,t)=>{const u=1-t;return u*u*u*a+3*u*u*t*b+3*u*t*t*c+t*t*t*d};
const animate=(ms,frame,done)=>{const start=performance.now();function tick(now){const t=Math.min(1,(now-start)/ms);frame(t);if(t<1)requestAnimationFrame(tick);else done()}requestAnimationFrame(tick)};
function finish(delay){setTimeout(()=>{stage.replaceChildren();stage.classList.remove('active');busy=false;sync()},delay)}
function lost(w,h,bottom=false){return put('spy-missile-lost','[ TARGET LOST ]',w*.5,bottom?h*.82:h*.18)}
function lock(target){const mark=put('spy-missile-lock','⊕',target.px,target.py);mark.style.width=Math.max(28,target.width)+'px';mark.style.height=Math.max(28,target.height)+'px'}
function fragments(x,y,color,count=25,spread=100,cls='spy-weapon-fragment'){
 for(let i=0;i<count;i++){const e=put(cls,'',x,y),a=Math.random()*Math.PI*2,r=spread*(.25+Math.random()*.75);e.style.background=color;e.style.setProperty('--dx',Math.cos(a)*r+'px');e.style.setProperty('--dy',Math.sin(a)*r+'px');e.style.setProperty('--spin',(Math.random()*900-450)+'deg')}
}
/* V33 launch positions */
const launchSites=[['left',.55],['left',.67],['left',.79],['left',.91],['right',.55],['right',.67],['right',.79],['right',.91]];
let lastLaunch=-1;
function launchPoint(w,h){let i=Math.floor(Math.random()*(launchSites.length-1));if(i>=lastLaunch)i++;lastLaunch=i;const [side,y]=launchSites[i];return [side==='left'?-Math.max(40,w*.12):w+Math.max(40,w*.12),h*y]}
function missile(target,w,h){if(target)lock(target);const [x0,y0]=launchPoint(w,h),rocket=put('spy-missile-projectile','🚀',x0,y0),message=target?null:lost(w,h);
 const tx=target?target.px:x0+(x0<w*.5?w:-w)*1.25,ty=target?target.py:y0+(y0<h*.5?h:-h)*.65,cx=(x0+tx)*.5,cy=(y0+ty)*.5-h*.42;
 const position=t=>{let x=bez(x0,cx,tx,t),y=bez(y0,cy,ty,t);if(!target){x+=Math.sin(t*22)*w*.10*(1-t*.35);y+=Math.sin(t*31)*h*.12*(1-t*.3)}return [x,y]};
 animate(target?2000:2600,t=>{const [x,y]=position(t),[nx,ny]=position(Math.min(1,t+.005));move(rocket,x,y,Math.atan2(ny-y,nx-x)*180/Math.PI+45)},()=>{rocket.remove();if(target){put('spy-missile-hit','💥',tx,ty);const colors=['#ffd166','#ef476f','#06d6a0','#118ab2','#fff','#f78c36'];for(let i=0;i<32;i++)fragments(tx,ty,colors[i%colors.length],1,Math.min(w,h)*.3,'spy-confetti')}else message?.classList.add('final');finish(target?1100:1400)})}
function vegetable(target,w,h){const [emoji,color]=produce[Math.floor(Math.random()*produce.length)],[x0,y0]=launchPoint(w,h),veg=put('spy-vegetable',emoji,x0,y0);veg.style.setProperty('--veg-color',color);if(target)lock(target);
 const tx=target?target.px:w-x0,ty=target?target.py:h-y0;
 if(target){animate(1600,t=>{const x=x0+(tx-x0)*t,y=y0+(ty-y0)*t-Math.min(h*.22,Math.max(0,Math.min(y0,ty)-h*.12))*4*t*(1-t);move(veg,x,y,t*800)},()=>{veg.remove();const splash=makeSplash(tx,ty,color,w,h);fragments(tx,ty,color,15,Math.min(w,h)*.24);finish(2400)})}
 else{let bounce=0;const floor=h*.86,midX=w*.5,exitX=x0<w*.5?w*1.2:-w*.2;animate(2600,t=>{let x,y;if(t<.52){const p=t/.52;x=x0+(midX-x0)*p;y=y0+(floor-y0)*p-h*.22*4*p*(1-p)}else{const p=(t-.52)/.48;x=midX+(exitX-midX)*p;y=floor-h*.30*4*p*(1-p)+h*.22*p}if(t>=.52&&!bounce){bounce=1;const e=put('spy-vegetable-bounce','✴',midX,floor);e.style.color=color}move(veg,x,y,t*1100)},()=>{veg.remove();finish(350)})}}
/* V27 splash and laser tuning */
function makeSplash(x,y,color,w,h){
 const NS='http://www.w3.org/2000/svg',svg=document.createElementNS(NS,'svg');svg.classList.add('spy-vegetable-splash','spy-splash-v27');svg.setAttribute('viewBox','0 0 220 220');svg.setAttribute('aria-hidden','true');svg.style.left=x+'px';svg.style.top=y+'px';svg.style.setProperty('--splash',color);
 const paths=[
 'M108 35 C121 42 125 9 140 14 C155 19 139 53 154 57 C171 64 183 35 196 47 C207 58 176 78 184 94 C193 110 217 98 216 115 C215 134 184 122 177 139 C171 156 203 179 187 189 C171 199 156 167 143 177 C130 187 139 213 121 215 C104 216 110 185 93 178 C75 170 57 204 44 191 C30 176 67 158 53 142 C40 129 7 144 7 126 C7 109 43 116 49 98 C54 82 22 64 37 51 C51 38 72 67 84 57 C96 48 91 19 108 35 Z',
 'M28 37 C36 29 45 34 44 42 C43 50 30 52 25 46 C22 43 23 40 28 37 Z',
 'M188 16 C198 9 208 19 202 28 C195 38 181 32 185 22 Z',
 'M18 176 C29 169 38 182 30 190 C19 200 10 186 18 176 Z',
 'M198 199 C207 194 217 201 212 210 C207 218 195 215 196 207 Z',
 'M92 9 C100 1 108 7 105 15 C102 24 87 21 92 9 Z'];
 for(const d of paths){const p=document.createElementNS(NS,'path');p.setAttribute('d',d);p.setAttribute('fill',color);svg.append(p)}
 stage.append(svg);
 for(let i=0;i<8;i++){
  const drop=document.createElement('div');drop.className='spy-splash-drip';drop.style.background=color;drop.style.left=(x+(Math.random()-.5)*Math.min(w*.34,160))+'px';drop.style.top=(y+Math.random()*Math.min(h*.14,55))+'px';drop.style.setProperty('--drip-distance',(h+80)+'px');drop.style.animationDelay=(.55+Math.random()*.4)+'s';drop.style.animationDuration=(1.25+Math.random()*.55)+'s';drop.style.width=(5+Math.random()*10)+'px';drop.style.height=(13+Math.random()*22)+'px';stage.append(drop)
 }
 return svg;
}
function laser(target,w,h){
 if(target)lock(target);
 const x0=w*(.25+Math.random()*.5),y0=-h*.06,tx=target?target.px:w*(.2+Math.random()*.6),ty=target?target.py:h*1.25;
 const beam=put('spy-laser-beam','',x0,y0),tip=put('spy-laser-tip','✦',x0,y0),message=target?null:lost(w,h,true);
 function position(t){
  if(target){const sway=Math.sin(t*Math.PI*5.5)*Math.sin(Math.PI*t)*Math.min(w,h)*.085;const dx=tx-x0,dy=ty-y0,len=Math.hypot(dx,dy)||1;return [x0+dx*t-dy/len*sway,y0+dy*t+dx/len*sway]}
  return [curve(x0,w*.35,w*.65,tx,t)+Math.sin(t*19)*w*.06,curve(y0,h*.15,h*.85,ty,t)+Math.sin(t*24)*h*.06]
 }
 function beamTo(x,y){const dx=x-x0,dy=y-y0;beam.style.left=x0+'px';beam.style.top=y0+'px';beam.style.width=Math.hypot(dx,dy)+'px';beam.style.transform=`rotate(${Math.atan2(dy,dx)}rad)`;move(tip,x,y)}
 animate(target?1150:1550,t=>{const [x,y]=position(t);beamTo(x,y)},()=>{
  if(!target){tip.remove();beam.remove();message?.classList.add('final');finish(1200);return}
  const hit=put('spy-laser-impact spy-laser-impact-v27','✹',tx,ty);
  fragments(tx,ty,'#ff3030',25,Math.min(w,h)*.25,'spy-laser-spark');
  beamTo(tx,ty);
  setTimeout(()=>{tip.remove();beam.remove()},350);
  finish(1350)
 })
}
function launch(){if(busy)return;document.querySelector('[data-view="camera"]')?.click();busy=true;stage.replaceChildren();stage.classList.add('active');const w=stage.clientWidth||320,h=stage.clientHeight||240,people=window.spyVisionTargets?.()||[],target=people.length?people.reduce((a,b)=>a.width*a.height>=b.width*b.height?a:b):null,m=mode();if(m==='turtle')vegetable(target,w,h);else if(m==='thermal')laser(target,w,h);else missile(target,w,h)}
button.addEventListener('click',launch);
})();
