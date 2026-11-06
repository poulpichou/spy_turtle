(() => {
    const toggle=document.getElementById("sentinel-enabled"),status=document.getElementById("sentinel-status");
    if(!toggle)return;
    async function request(path,body){return turtleRequest(path,body===undefined?null:body)}
    async function refresh(){try{const data=await request("/sentinel/status");toggle.checked=!!data.enabled;status.textContent="";status.hidden=true}catch(error){status.hidden=false;status.textContent=error.message}}
    toggle.onchange=async()=>{toggle.disabled=true;try{const data=await request("/sentinel/enable",{enabled:toggle.checked});status.textContent="";status.hidden=true}catch(error){status.hidden=false;status.textContent=error.message;await refresh()}finally{toggle.disabled=false}};
    document.addEventListener("transportchange",refresh);refresh();
})();
