const API_BASE="http://spyturtle:8000";

async function getStatus(){
    const r=await fetch(`${API_BASE}/state`);
    return await r.json();
}

async function sendCommand(type,value){
    await fetch(`${API_BASE}/command`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({type,value})
    });
}