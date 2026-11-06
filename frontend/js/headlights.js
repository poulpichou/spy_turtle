(() => {
    const button=document.getElementById('headlights-toggle');if(!button)return;
    let enabled=false,idle=false,busy=false;
    function render(){button.disabled=idle||busy;button.classList.toggle('active',enabled&&!idle);button.setAttribute('aria-pressed',String(enabled&&!idle));button.title=idle?'Disable Idle mode to use headlights':'Headlights (LEDs 13–26)'}
    async function request(enabled){
        if(typeof transportMode!=='undefined'&&transportMode==='bluetooth')throw Error('Headlights require Wi-Fi');
        const response=await fetch('/brain/headlights',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled})});
        const data=await response.json();if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);return data;
    }
    async function refresh(){
        try{const response=await fetch('/brain/moods',{cache:'no-store'});if(response.ok){const data=await response.json();enabled=!!data.headlights_enabled}}
        catch(error){console.warn('[LIGHTS] status',error)}render();
    }
    button.onclick=async()=>{if(idle||busy)return;busy=true;render();try{const data=await request(!enabled);enabled=!!data.headlights_enabled}catch(error){console.error('[LIGHTS]',error);alert(error.message)}finally{busy=false;render()}};
    document.addEventListener('turtlepowerchange',event=>{idle=!!event.detail.idle_mode;if(idle)enabled=false;render();if(!idle)refresh()});
    document.addEventListener('transportchange',refresh);
    render();refresh();
})();
