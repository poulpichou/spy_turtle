/* V25: face-locked missile, or erratic target-lost exit. Sound remains in head-tools.js. */
(()=>{'use strict';const view=document.getElementById('camera-view'),button=document.getElementById('head-missile');if(!view||!button)return;
const stage=document.createElement('div');stage.className='spy-missile-stage';stage.setAttribute('aria-hidden','true');view.append(stage);let busy=false;
const put=(cls,text,x,y)=>{const e=document.createElement('div');e.className=cls;e.textContent=text;e.style.left=x+'px';e.style.top=y+'px';stage.append(e);return e};
function launch(){if(busy)return;document.querySelector('[data-view="camera"]')?.click();busy=true;stage.replaceChildren();stage.classList.add('active');const w=stage.clientWidth||320,h=stage.clientHeight||240,people=window.spyVisionTargets?.()||[],target=people.length?people.reduce((a,b)=>a.width*a.height>=b.width*b.height?a:b):null;
if(target){const mark=put('spy-missile-lock','⊕',target.px,target.py);mark.style.width=Math.max(28,target.width)+'px';mark.style.height=Math.max(28,target.height)+'px'}
const rocket=put('spy-missile-projectile','🚀',w*.1,h*.88);const message=!target?put('spy-missile-lost','[ TARGET LOST ]',w*.5,h*.2):null;
const x0=w*.1,y0=h*.88,tx=target?target.px:w*1.2,ty=target?target.py:-h*.3,cx=target?w*.4:w*.83,cy=target?h*.02:h*.95;
const start=performance.now(),duration=target?2000:2600;
function tick(now){const t=Math.min(1,(now-start)/duration),u=1-t;let x=u*u*x0+2*u*t*cx+t*t*tx,y=u*u*y0+2*u*t*cy+t*t*ty;
if(!target){x+=Math.sin(t*22)*w*.10*(1-t*.35);y+=Math.sin(t*31)*h*.12*(1-t*.3)}
const dt=.005,t2=Math.min(1,t+dt),v=1-t2;let nx=v*v*x0+2*v*t2*cx+t2*t2*tx,ny=v*v*y0+2*v*t2*cy+t2*t2*ty;if(!target){nx+=Math.sin(t2*22)*w*.10*(1-t2*.35);ny+=Math.sin(t2*31)*h*.12*(1-t2*.3)}
rocket.style.left=x+'px';rocket.style.top=y+'px';rocket.style.transform=`translate(-50%,-50%) rotate(${Math.atan2(ny-y,nx-x)*180/Math.PI+45}deg)`;
if(t<1){requestAnimationFrame(tick);return}rocket.remove();if(target){put('spy-missile-hit','💥',tx,ty);const colors=['#ffd166','#ef476f','#06d6a0','#118ab2','#fff','#f78c36'];for(let i=0;i<32;i++){const bit=put('spy-confetti','',tx,ty),angle=Math.random()*Math.PI*2,dist=35+Math.random()*Math.min(w,h)*.28;bit.style.background=colors[i%colors.length];bit.style.setProperty('--dx',Math.cos(angle)*dist+'px');bit.style.setProperty('--dy',Math.sin(angle)*dist+'px');bit.style.setProperty('--spin',Math.round(Math.random()*900-450)+'deg')}}else message?.classList.add('final');setTimeout(()=>{stage.replaceChildren();stage.classList.remove('active');busy=false},target?1100:1400)}requestAnimationFrame(tick)}
button.addEventListener('click',launch);
})();
