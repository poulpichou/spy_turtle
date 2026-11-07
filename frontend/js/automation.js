(() => {
    const head=document.getElementById("automation-head"),sound=document.getElementById("automation-sounds"),movement=document.getElementById("automation-movement"),status=document.getElementById("automation-status");
    if(!head||!sound)return;
    async function request(path,body){return turtleRequest(path,body===undefined?null:body)}
    async function refresh(){try{const data=await request("/brain/moods");head.checked=!!data.enable_head_movements;status.textContent="";status.hidden=true}catch(error){head.disabled=true;status.hidden=false;status.textContent=`Mood Engine unavailable: ${error.message}`}}
    head.onchange=async()=>{head.disabled=true;try{const data=await request("/brain/head-movements",{enabled:head.checked});head.checked=!!data.enable_head_movements}catch(error){status.hidden=false;status.textContent=error.message}finally{head.disabled=false}};
    async function refreshSounds(){try{const data=await turtleRequest("/automation/status");sound.checked=!!(data.automation_sounds??data.sounds)}catch(error){console.warn("[AUTOMATION SOUNDS]",error)}}
    sound.onchange=async()=>{const next=sound.checked;sound.disabled=true;try{const data=await turtleRequest("/automation/sounds",{enabled:next});sound.checked=!!(data.automation_sounds??data.sounds)}catch(error){status.hidden=false;status.textContent=error.message;sound.checked=!next}finally{sound.disabled=false;document.dispatchEvent(new Event("automationchanged"))}};
    refreshSounds();document.addEventListener("transportchange",refreshSounds);
    if(movement){movement.disabled=true;movement.checked=false}
    refresh();document.addEventListener("transportchange",refresh);
})();
