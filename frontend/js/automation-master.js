(() => {
    const button=document.getElementById("automation-master"),admin=document.getElementById("automation-master-admin");
    const greet=document.getElementById("sentinel-enabled"),head=document.getElementById("automation-head"),sound=document.getElementById("automation-sounds"),movement=document.getElementById("automation-movement"),status=document.getElementById("automation-status");
    if(!button||!admin)return;
    let enabled=true,idle=false,busy=false;
    function render(){
        button.classList.toggle("active",enabled&&!idle);button.disabled=busy||idle;button.setAttribute("aria-pressed",String(enabled&&!idle));
        admin.checked=enabled;admin.disabled=busy||idle;
        for(const c of [greet,head,sound])if(c)c.disabled=busy||idle||!enabled;
        if(movement)movement.disabled=true;
    }
    async function refresh(){try{const data=await turtleRequest("/automation/status");enabled=!!(data.automation_enabled??data.enabled);if(data.automation_sounds!==undefined&&sound)sound.checked=!!data.automation_sounds;if(data.sounds!==undefined&&sound)sound.checked=!!data.sounds;status.hidden=true}catch(error){console.warn("[AUTOMATION]",error)}render()}
    async function set(next){if(busy||idle)return;busy=true;render();try{const data=await turtleRequest("/automation/enable",{enabled:next});enabled=!!(data.automation_enabled??data.enabled);status.hidden=true}catch(error){status.hidden=false;status.textContent=error.message}finally{busy=false;render()}}
    button.onclick=()=>set(!enabled);admin.onchange=()=>set(admin.checked);
    document.addEventListener("turtlepowerchange",event=>{idle=!!event.detail.idle_mode;render()});
    document.addEventListener("transportchange",refresh);
    document.addEventListener("automationchanged",refresh);
    render();refresh();
})();
