const API=`http://${location.hostname}:8000`;

async function getStatus(){
    const r=await fetch(`${API}/state`);
    return await r.json();
}

async function sendCommand(type,value){
    console.log("[FRONTEND COMMAND]",type,value);

    const r=await fetch(`${API}/command`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({type,value})
    });

    console.log("[FRONTEND RESPONSE]",await r.json());
}