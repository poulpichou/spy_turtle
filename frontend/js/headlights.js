(() => {
    const button=document.getElementById('headlights-toggle');if(!button)return;
    let enabled=false,idle=false,busy=false;
    function render(){button.disabled=idle||busy;button.classList.toggle('active',enabled&&!idle);button.setAttribute('aria-pressed',String(enabled&&!idle));button.title=idle?'Disable Idle mode to use headlights':'Headlights (LEDs 14–25)'}
    async function request(enabled){return turtleRequest("/brain/headlights",{enabled})}
    async function refresh(){
        try{const data=await turtleRequest("/brain/moods");enabled=!!data.headlights_enabled}
        catch(error){console.warn("[LIGHTS] status",error)}
        render();
    }
    button.onclick=async()=>{if(idle||busy)return;busy=true;render();try{const data=await request(!enabled);enabled=!!data.headlights_enabled}catch(error){console.error('[LIGHTS]',error);alert(error.message)}finally{busy=false;render()}};
    document.addEventListener('turtlepowerchange',event=>{idle=!!event.detail.idle_mode;if(idle)enabled=false;render();if(!idle)refresh()});
    document.addEventListener('transportchange',refresh);
    render();refresh();
})();
