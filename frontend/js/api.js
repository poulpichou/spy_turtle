const API="";

async function getStatus(){
    if(transportMode==="bluetooth")return readBluetoothState();
    const response=await fetch(`${API}/state`);
    if(!response.ok)throw new Error(`State request failed: ${response.status}`);
    return response.json();
}

async function getAssets(){
    const response=await fetch(`${API}/assets`);
    if(!response.ok)throw new Error(`Assets request failed: ${response.status}`);
    return response.json();
}

async function sendCommand(type,value="",extra={}){
    console.log("[FRONTEND COMMAND]",transportLabel(),type,value,extra);
    if(transportMode==="bluetooth"){
        await writeBluetoothCommand({type,value,extra});
        return {ok:true,transport:"bluetooth"};
    }
    const response=await fetch(`${API}/command`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({type,value,extra})
    });
    const data=await response.json();
    if(!response.ok){
        const message=data.detail||`Command failed: ${response.status}`;
        console.error("[FRONTEND ERROR]",message);
        throw new Error(message);
    }
    console.log("[FRONTEND RESPONSE]",data);
    return data;
}
