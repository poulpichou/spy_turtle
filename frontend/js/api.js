const API_MODE="robot";
const API_URL="http://spyturtle:8000";

async function getStatus(){
    if(API_MODE==="robot"){
        const r=await fetch(API_URL+"/state");
        return await r.json();
    }

    return {
        battery:fakeRobot.battery,
        wifi:true,
        emotion:fakeRobot.emotion,
        led_mode:fakeRobot.led_mode,
        motion:fakeRobot.motion
    };
}

async function sendCommand(type,value){
    if(API_MODE!=="robot"){
        fakeRobot.receiveCommand(type,value);
        return;
    }

    let url=null;

    if(type==="move") url="/move/"+value;
    if(type==="face") url="/emotion/"+value.toLowerCase();
    if(type==="head") url="/camera/"+value;

    if(url)
        await fetch(API_URL+url,{method:"POST"});
}