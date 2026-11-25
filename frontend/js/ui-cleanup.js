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
  document.dispatchEvent(new Event('spyvisionchange'));
  if(enabled){stopCameraRefresh();if(view.classList.contains('active'))startThermal()}
  else{stopThermal();if(view.classList.contains('active'))startCameraRefresh()}
 };
 const saved=localStorage.getItem('spy_grid_vision_mode');
 if(saved==='thermal')window.spySetThermalVision(true);
 document.addEventListener('transportchange',()=>{if(thermalMode){stopCameraRefresh();if(view.classList.contains('active')){stopThermal();startThermal()}}});
})();
