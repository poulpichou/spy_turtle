const API="http://spyturtle:8000";

async function getStatus(){
    const r=await fetch(`${API}/state`);
    return await r.json();
}

async function sendCommand(type,value){
    console.log("COMMAND:",type,value);

    await fetch(`${API}/command`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({type,value})
    });
}