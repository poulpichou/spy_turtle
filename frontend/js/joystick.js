(() => {
    const pad=document.getElementById("drive-joystick"),knob=document.getElementById("drive-knob"),toggle=document.getElementById("drive-mode-toggle"),dpad=document.getElementById("drive-dpad");
    if(!pad||!knob||!toggle||!dpad)return;
    const TURN_SENSITIVITY=0.375; // +50% steering vs V5
    const STRAIGHT_CONE_DEGREES=0; // Steering dead cone around forward/backward axes
    const JOYSTICK_DEADZONE=0.12; // no movement within 12% of radius
    const JOYSTICK_MIN_OUTPUT=0.67; // 0.67 * 0.30 = 0.20 PWM at first movement
    let active=false,pointer=null,timer=null,x=0,y=0,busy=false;
    const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
    function render(){knob.style.transform=`translate(calc(-50% + ${x*100}%),calc(-50% + ${-y*100}%))`;knob.style.left=`${50+x*34}%`;knob.style.top=`${50-y*34}%`;knob.style.transform="translate(-50%,-50%)"}
    function speeds(){
        const magnitude=Math.hypot(x,y);
        if(magnitude<=JOYSTICK_DEADZONE)return [0,0];
        const scale=JOYSTICK_MIN_OUTPUT+(1-JOYSTICK_MIN_OUTPUT)*(magnitude-JOYSTICK_DEADZONE)/(1-JOYSTICK_DEADZONE);
        // Straight corridor +/-STRAIGHT_CONE_DEGREES; smooth steering beyond it.
        // Never normalize small steering into full motor power.
        const cone=Math.tan(STRAIGHT_CONE_DEGREES*Math.PI/180);
        const side=Math.max(0,Math.abs(x)-Math.abs(y)*cone);
        const steering=Math.sign(x)*side*TURN_SENSITIVITY;
        const forward=Math.sign(y)*scale*Math.min(1,Math.abs(y)/Math.max(JOYSTICK_DEADZONE,magnitude));
        const turn=steering*(0.25/(0.30*TURN_SENSITIVITY)); // cap pure turning at D-pad 0.25 PWM
        return [forward+turn,forward-turn].map(v=>Math.round(clamp(v,-1,1)*1000)/1000);
    }
    async function tick(){
        if(!active||busy)return;
        if(transportMode==="bluetooth"&&bluetoothPending>1)return;
        const [left,right]=speeds();
        busy=true;
        try{await sendCommand("move","joystick",{left,right})}
        catch(error){console.warn("[JOYSTICK] Command failed",error);release()}
        finally{busy=false}
    }
    function move(event){
        const rect=pad.getBoundingClientRect(),radius=rect.width/2;
        let dx=(event.clientX-(rect.left+radius))/radius,dy=((rect.top+radius)-event.clientY)/radius;
        const length=Math.hypot(dx,dy);
        if(length>1){dx/=length;dy/=length}
        x=dx;y=dy;render();
    }
    function release(){
        if(timer){clearInterval(timer);timer=null}
        const wasActive=active;active=false;pointer=null;x=0;y=0;render();
        if(wasActive)sendCommand("move","stop").catch(error=>console.warn("[SAFETY] Joystick stop failed; watchdog fallback",error));
    }
    pad.addEventListener("pointerdown",event=>{
        if(pointer!==null)return;
        event.preventDefault();if(typeof releaseMovement==="function"&&heldDirection)releaseMovement();
        pointer=event.pointerId;active=true;pad.setPointerCapture(pointer);move(event);tick();timer=setInterval(tick,300);
    });
    pad.addEventListener("pointermove",event=>{if(pointer===event.pointerId){event.preventDefault();move(event)}});
    pad.addEventListener("pointerup",event=>{if(pointer===event.pointerId)release()});
    pad.addEventListener("pointercancel",event=>{if(pointer===event.pointerId)release()});
    pad.addEventListener("lostpointercapture",()=>release());
    toggle.addEventListener("click",()=>{
        release();if(typeof releaseMovement==="function"&&heldDirection)releaseMovement();
        const enabled=pad.hidden;pad.hidden=!enabled;dpad.hidden=enabled;
        toggle.textContent=enabled?"✥":"🎮";toggle.setAttribute("aria-pressed",String(enabled));toggle.setAttribute("aria-label",enabled?"Switch to D-pad":"Switch to joystick");toggle.title=enabled?"Switch to D-pad":"Switch to joystick";
    });
    window.addEventListener("blur",release);
    document.addEventListener("visibilitychange",()=>{if(document.hidden)release()});
    document.addEventListener("transportchange",release);
    render();
})();
