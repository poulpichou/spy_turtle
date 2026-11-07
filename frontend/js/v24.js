(() => {
 const slider=document.getElementById("headlight-intensity-slider"),label=document.getElementById("headlight-intensity-value");
 async function intensity(method,value){
  const r=await fetch("/admin/leds/headlights/intensity",{method,headers:{"Content-Type":"application/json"},body:method==="POST"?JSON.stringify({intensity:value}):undefined});
  const d=await r.json();if(!r.ok)throw Error(d.detail||r.status);return d;
 }
 if(slider){slider.oninput=()=>label.textContent=slider.value+"%";slider.onchange=()=>intensity("POST",Number(slider.value)).catch(console.error);intensity("GET").then(d=>{slider.value=d.intensity;label.textContent=d.intensity+"%"}).catch(console.warn)}
 const adaptive=document.getElementById("adaptive-volume"),master=document.getElementById("automation-master-admin");
 function sync(){if(adaptive&&master){adaptive.disabled=!master.checked;adaptive.title=adaptive.disabled?"Enable automation first":""}}
 master?.addEventListener("change",()=>setTimeout(sync,200));setInterval(sync,2000);sync();
 function sound(v){return v==null?"No measurement":v<.02?"Quiet":v<.05?"Slightly loud":v<.10?"Loud":"Very loud"}
 async function status(){
  if(!document.getElementById("status-view")?.classList.contains("active"))return;
  try{
   const r=await fetch("/admin/audio/adaptive",{cache:"no-store"});if(!r.ok)return;const d=await r.json();
   for(const [id,value] of Object.entries({"health-ambient-sound":sound(d.ambient_rms),"health-ambient-rms":d.ambient_rms??"--","health-adaptive-boost":"+"+(master?.checked?d.boost||0:0)+"%"})){const e=document.getElementById(id);if(e)e.textContent=value}
  }catch(e){console.warn("[AUDIO STATUS]",e)}
 }
 setInterval(status,3000);status();
})();
