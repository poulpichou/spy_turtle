/* V24: one Camera view for all vision modes, plus a playful missile overlay. */
(()=>{
 const view=document.getElementById('camera-view'),rgb=document.getElementById('camera-stream'),thermal=document.getElementById('thermal-stream');
 if(!view||!rgb||!thermal)return;
 let thermalMode=false;
 window.spyIsThermalVision=()=>thermalMode;
 window.spySetThermalVision=enabled=>{
  enabled=!!enabled;
  if(thermalMode===enabled)return;
  thermalMode=enabled;
  rgb.hidden=enabled;thermal.hidden=!enabled;
  if(enabled){stopCameraRefresh();if(view.classList.contains('active'))startThermal()}
  else{stopThermal();if(view.classList.contains('active'))startCameraRefresh()}
 };
 const saved=localStorage.getItem('spy_grid_vision_mode');
 if(saved==='thermal')window.spySetThermalVision(true);
 const overlay=document.createElement('div');overlay.className='spy-missile-stage';overlay.setAttribute('aria-hidden','true');view.append(overlay);
 const targets=[{x:.18,y:.24,emoji:'🎯'},{x:.76,y:.32,emoji:'🎯'},{x:.59,y:.73,emoji:'🎯'}];
 let busy=false;
 function launch(){
  if(busy)return;
  document.querySelector('[data-view="camera"]')?.click();
  busy=true;overlay.replaceChildren();overlay.classList.add('active');
  const w=overlay.clientWidth||320,h=overlay.clientHeight||240;
  const target=targets[Math.floor(Math.random()*targets.length)],tx=target.x*w,ty=target.y*h;
  for(const t of targets){
   const el=document.createElement('div');el.className='spy-missile-target';el.textContent=t.emoji;
   el.style.left=t.x*100+'%';el.style.top=t.y*100+'%';overlay.append(el);
  }
  const rocket=document.createElement('div');rocket.className='spy-missile-projectile';rocket.textContent='🚀';overlay.append(rocket);
  const x0=w*.10,y0=h*.88,cx=w*(.36+Math.random()*.16),cy=h*.02;
  const start=performance.now();
  function tick(now){
   const t=Math.min(1,(now-start)/2000),u=1-t;
   const x=u*u*x0+2*u*t*cx+t*t*tx,y=u*u*y0+2*u*t*cy+t*t*ty;
   const dx=2*u*(cx-x0)+2*t*(tx-cx),dy=2*u*(cy-y0)+2*t*(ty-cy);
   rocket.style.left=x+'px';rocket.style.top=y+'px';rocket.style.transform=`translate(-50%,-50%) rotate(${Math.atan2(dy,dx)*180/Math.PI+45}deg)`;
   if(t<1){requestAnimationFrame(tick);return}
   rocket.remove();
   const hit=document.createElement('div');hit.className='spy-missile-hit';hit.textContent='💥';hit.style.left=tx+'px';hit.style.top=ty+'px';overlay.append(hit);
   const palette=['#ffd166','#ef476f','#06d6a0','#118ab2','#ffffff','#f78c36'];
   for(let i=0;i<32;i++){
    const bit=document.createElement('i');bit.className='spy-confetti';
    const angle=Math.random()*Math.PI*2,dist=35+Math.random()*Math.min(w,h)*.28;
    bit.style.left=tx+'px';bit.style.top=ty+'px';bit.style.background=palette[i%palette.length];
    bit.style.setProperty('--dx',Math.cos(angle)*dist+'px');bit.style.setProperty('--dy',Math.sin(angle)*dist+'px');
    bit.style.setProperty('--spin',Math.round(Math.random()*900-450)+'deg');overlay.append(bit);
   }
   setTimeout(()=>{overlay.replaceChildren();overlay.classList.remove('active');busy=false},1100);
  }
  requestAnimationFrame(tick);
 }
 const missile=document.getElementById('head-missile');
 if(missile)missile.addEventListener('click',launch);
})();
