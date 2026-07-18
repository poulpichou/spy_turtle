const API="";

async function getStatus(){
    const r=await fetch("/state");
    return await r.json();
}

async function sendCommand(type,value){
    console.log("COMMAND:",type,value);

    await fetch("/command",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({type,value})
    });
}