const API_BASE="http://spyturtle:8000";

async function getStatus(){
    const r=await fetch(`${API_BASE}/state`);
    return await r.json();
}

async function sendCommand(type,value){
    console.log("COMMAND:",type,value);

    let url=null;

    if(type==="move") url=`/move/${value}`;
    if(type==="face") url=`/emotion/${value}`;
    if(type==="led") url=`/led/${value}`;

    if(!url) return;

    await fetch(API_BASE+url,{method:"POST"});
}