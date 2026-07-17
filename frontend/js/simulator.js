const fakeRobot={
    battery:92,
    emotion:"neutral",
    led_mode:"off",
    motion:"stop",
    head:"center",

    receiveCommand(type,value){
        console.log("Robot received:",type,value);
        if(type==="move"){
            this.motion=value;
        }
        if(type==="head"){
            this.head=value;
        }
        if(type==="face"){
            this.emotion=value;
        }
        if(type==="led"){
            this.led_mode=value;
        }
    }
};


setInterval(()=>{
    const emotions=["neutral","happy","curious","sleepy"];

    if(Math.random()<0.2){
        fakeRobot.emotion=emotions[Math.floor(Math.random()*emotions.length)];
    }
},5000);


console.log(fakeRobot);