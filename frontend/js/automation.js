(() => {
    const head=document.getElementById("automation-head"),sound=document.getElementById("automation-sounds"),movement=document.getElementById("automation-movement"),status=document.getElementById("automation-status");
    if(!head||!sound)return;
    async function request(path,body){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth")throw Error("Wi-Fi required");
        const response=await fetch(path,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined,cache:"no-store"});
        const data=await response.json();if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);return data;
    }
    async function refresh(){try{const data=await request("/brain/moods");head.checked=!!data.enable_head_movements;status.textContent="";status.hidden=true}catch(error){head.disabled=true;status.hidden=false;status.textContent=`Mood Engine unavailable: ${error.message}`}}
    head.onchange=async()=>{head.disabled=true;try{const data=await request("/brain/head-movements",{enabled:head.checked});head.checked=!!data.enable_head_movements}catch(error){status.hidden=false;status.textContent=error.message}finally{head.disabled=false}};
    sound.checked=localStorage.getItem("spy_turtle_automation_sounds")!=="false";
    sound.onchange=()=>localStorage.setItem("spy_turtle_automation_sounds",String(sound.checked));
    if(movement){movement.disabled=true;movement.checked=false}
    refresh();document.addEventListener("transportchange",refresh);
})();
