(() => {
    const toggle=document.getElementById("sentinel-enabled"),status=document.getElementById("sentinel-status");
    if(!toggle)return;
    async function request(path,body){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth")throw Error("Sentinel settings require Wi-Fi");
        const response=await fetch(path,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined,cache:"no-store"});
        const data=await response.json();if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);return data;
    }
    async function refresh(){try{const data=await request("/sentinel/status");toggle.checked=!!data.enabled;status.textContent="";status.hidden=true}catch(error){status.hidden=false;status.textContent=error.message}}
    toggle.onchange=async()=>{toggle.disabled=true;try{const data=await request("/sentinel/enable",{enabled:toggle.checked});status.textContent="";status.hidden=true}catch(error){status.hidden=false;status.textContent=error.message;await refresh()}finally{toggle.disabled=false}};
    document.addEventListener("transportchange",refresh);refresh();
})();
