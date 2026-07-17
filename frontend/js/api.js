const API_MODE="simulation";

async function getStatus(){
    if(API_MODE==="simulation"){
        return {
            battery:fakeRobot.battery,
            wifi:true,
            connection:"online",
            emotion:fakeRobot.emotion,
            led_mode:fakeRobot.led_mode,
            motion:fakeRobot.motion,
            head:fakeRobot.head
        }
    }
}

async function sendCommand(type,value){
    console.log("COMMAND:",type,value);
    if(API_MODE==="simulation"){
        fakeRobot.receiveCommand(type,value);
    }
}