/* V26: mode-aware playful camera projectiles; visual only, never controls hardware. */
(()=>{'use strict';
const view=document.getElementById('camera-view'),button=document.getElementById('head-missile');if(!view||!button)return;
const stage=document.createElement('div');stage.className='spy-missile-stage spy-weapon-stage';stage.setAttribute('aria-hidden','true');view.append(stage);
const vegetables=[['🥕','#f58a27'],['🥦','#4d9b37'],['🥬','#7fc957'],['🥒','#71a83c'],['🌶️','#e33a32'],['🫑','#50a83e'],['🌽','#efc849'],['🍆','#783ca1'],['🥔','#b99466'],['🧅','#d6b88a'],['🧄','#e6e0ce'],['🍅','#ec4136'],['🫛','#68ad49'],['🍄','#d94b40']];
let busy=false;const mode=()=>{const m=localStorage.getItem('spy_grid_vision_mode');return m==='turtle'||m==='thermal'?m:'robot'};
function sync(){const m=mode();button.textContent=m==='turtle'?'🥕':m==='thermal'?'🔫':'🚀';button.title=m==='turtle'?'Launch a random vegetable':m==='thermal'?'Fire thermal laser':'Launch missile';button.setAttribute('aria-label',button.title)}
sync();document.addEventListener('click',e=>{if(e.target.closest?.('.spy-vision-segment'))queueMicrotask(sync)});window.addEventListener('storage',sync);
const put=(cls,text,x,y)=>{const e=document.createElement('div');e.className=cls;e.textContent=text;e.style.left=x+'px';e.style.top=y+'px';stage.append(e);return e};
const move=(e,x,y,deg=0)=>{e.style.left=x+'px';e.style.top=y+'px';e.style.transform=`translate(-50%,-50%) rotate(${deg}deg)`};
const bez=(a,b,c,t)=>{const u=1-t;return u*u*a+2*u*t*b+t*t*c};
const curve=(a,b,c,d,t)=>{const u=1-t;return u*u*u*a+3*u*u*t*b+3*u*t*t*c+t*t*t*d};
const animate=(ms,frame,done)=>{const start=performance.now();function tick(now){const t=Math.min(1,(now-start)/ms);frame(t);if(t<1)requestAnimationFrame(tick);else done()}requestAnimationFrame(tick)};
function finish(delay){setTimeout(()=>{stage.replaceChildren();stage.classList.remove('active');busy=false;sync()},delay)}
function lost(w,h){return put('spy-missile-lost','[ TARGET LOST ]',w*.5,h*.18)}
function lock(target){const mark=put('spy-missile-lock','⊕',target.px,target.py);mark.style.width=Math.max(28,target.width)+'px';mark.style.height=Math.max(28,target.height)+'px'}
function fragments(x,y,color,count=25,spread=100,cls='spy-weapon-fragment'){
 for(let i=0;i<count;i++){const e=put(cls,'',x,y),a=Math.random()*Math.PI*2,r=spread*(.25+Math.random()*.75);e.style.background=color;e.style.setProperty('--dx',Math.cos(a)*r+'px');e.style.setProperty('--dy',Math.sin(a)*r+'px');e.style.setProperty('--spin',(Math.random()*900-450)+'deg')}
}
function missile(target,w,h){if(target)lock(target);const rocket=put('spy-missile-projectile','🚀',w*.1,h*.88),message=target?null:lost(w,h);
 const x0=w*.1,y0=h*.88,tx=target?target.px:w*1.2,ty=target?target.py:-h*.3,cx=target?w*.4:w*.83,cy=target?h*.02:h*.95;
 const position=t=>{let x=bez(x0,cx,tx,t),y=bez(y0,cy,ty,t);if(!target){x+=Math.sin(t*22)*w*.10*(1-t*.35);y+=Math.sin(t*31)*h*.12*(1-t*.3)}return [x,y]};
 animate(target?2000:2600,t=>{const [x,y]=position(t),[nx,ny]=position(Math.min(1,t+.005));move(rocket,x,y,Math.atan2(ny-y,nx-x)*180/Math.PI+45)},()=>{rocket.remove();if(target){put('spy-missile-hit','💥',tx,ty);const colors=['#ffd166','#ef476f','#06d6a0','#118ab2','#fff','#f78c36'];for(let i=0;i<32;i++)fragments(tx,ty,colors[i%colors.length],1,Math.min(w,h)*.3,'spy-confetti')}else message?.classList.add('final');finish(target?1100:1400)})}
function vegetable(target,w,h){const [emoji,color]=vegetables[Math.floor(Math.random()*vegetables.length)],veg=put('spy-vegetable',emoji,w*.12,h*.9);veg.style.setProperty('--veg-color',color);if(target)lock(target);
 const x0=w*.12,y0=h*.90,tx=target?target.px:w*.66,ty=target?target.py:h*.87;
 if(target){animate(1600,t=>{const x=x0+(tx-x0)*t,y=y0+(ty-y0)*t-h*.55*4*t*(1-t);move(veg,x,y,t*800)},()=>{veg.remove();const splash=put('spy-vegetable-splash','',tx,ty);splash.style.setProperty('--splash',color);fragments(tx,ty,color,38,Math.min(w,h)*.46);finish(1250)})}
 else{let bounce=0;const floor=h*.86;animate(2600,t=>{let x,y;if(t<.52){const p=t/.52;x=x0+(w*.57-x0)*p;y=y0+(floor-y0)*p-h*.6*4*p*(1-p)}else{const p=(t-.52)/.48;x=w*.57+(w*.62)*p;y=floor-h*.30*4*p*(1-p)+h*.22*p}if(t>=.52&&!bounce){bounce=1;const e=put('spy-vegetable-bounce','✴',w*.57,floor);e.style.color=color}move(veg,x,y,t*1100)},()=>{veg.remove();finish(350)})}}
function laser(target,w,h){if(target)lock(target);const x0=w*.1,y0=h*.88,tx=target?target.px:w*1.25,ty=target?target.py:-h*.25;const beam=put('spy-laser-beam','',x0,y0),tip=put('spy-laser-tip','✦',x0,y0),message=target?null:lost(w,h);
 function position(t){if(target)return [x0+(tx-x0)*t,y0+(ty-y0)*t];return [curve(x0,w*.35,w*.8,tx,t)+Math.sin(t*19)*w*.06,curve(y0,h*.15,h*.92,ty,t)+Math.sin(t*24)*h*.06]}
 animate(target?780:1550,t=>{const [x,y]=position(t),dx=x-x0,dy=y-y0;beam.style.left=x0+'px';beam.style.top=y0+'px';beam.style.width=Math.hypot(dx,dy)+'px';beam.style.transform=`rotate(${Math.atan2(dy,dx)}rad)`;move(tip,x,y)},()=>{tip.remove();beam.remove();if(target){put('spy-laser-impact','✹',tx,ty);fragments(tx,ty,'#ff3030',25,Math.min(w,h)*.25,'spy-laser-spark')}else message?.classList.add('final');finish(target?800:1200)})}
function launch(){if(busy)return;document.querySelector('[data-view="camera"]')?.click();busy=true;stage.replaceChildren();stage.classList.add('active');const w=stage.clientWidth||320,h=stage.clientHeight||240,people=window.spyVisionTargets?.()||[],target=people.length?people.reduce((a,b)=>a.width*a.height>=b.width*b.height?a:b):null,m=mode();if(m==='turtle')vegetable(target,w,h);else if(m==='thermal')laser(target,w,h);else missile(target,w,h)}
button.addEventListener('click',launch);
})();
