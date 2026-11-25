/* V23: head calibration shortcut and playful sound action. */
(()=>{
 const card=document.querySelector('.head-control-card'),calibrate=document.getElementById('head-reset');
 if(!card||!calibrate)return;
 calibrate.textContent='↔';calibrate.title='Calibrate pan center';calibrate.setAttribute('aria-label','Calibrate pan center');
 calibrate.onclick=()=>{
  if(document.querySelector('.spy-head-calibration-modal'))return;
  const control=document.getElementById('pan-center-slider')?.closest('.admin-slider');
  if(!control)return;
  const parent=control.parentNode,next=control.nextSibling;
  const overlay=document.createElement('div');overlay.className='spy-grid-modal spy-head-calibration-modal';overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-label','Pan center calibration');
  const panel=document.createElement('div');panel.className='spy-grid-modal-panel';
  const heading=document.createElement('div');heading.className='spy-grid-modal-heading';heading.textContent='↔ Pan center calibration';
  const close=document.createElement('button');close.type='button';close.textContent='×';close.setAttribute('aria-label','Close');
  const dismiss=()=>{parent.insertBefore(control,next);overlay.remove()};
  close.onclick=dismiss;heading.append(close);panel.append(heading,control);
  overlay.append(panel);overlay.onclick=e=>{if(e.target===overlay)dismiss()};
  document.body.append(overlay);
  if(typeof panOffsetLoad==='function')panOffsetLoad();
 };
 const missile=document.createElement('button');missile.id='head-missile';missile.type='button';missile.textContent='🚀';missile.title='Play a random robot sound';missile.setAttribute('aria-label','Play a random robot sound');
 missile.onclick=async()=>{
  if(missile.disabled)return;
  const sounds=['robot1','robot2','robot3','robot4'];
  missile.disabled=true;
  try{await sendCommand('sound',sounds[Math.floor(Math.random()*sounds.length)])}
  catch(error){if(typeof showCommandError==='function')showCommandError(error);else console.error(error)}
  finally{missile.disabled=false}
 };
 card.append(missile);
})();
