(() => {
    const pad=document.getElementById("drive-joystick"),knob=document.getElementById("drive-knob"),toggle=document.getElementById("drive-mode-toggle"),dpad=document.getElementById("drive-dpad");
    if(!pad||!knob||!toggle||!dpad)return;
    const TURN_SENSITIVITY=0.375; // +50% steering vs V5
    const STRAIGHT_CONE_DEGREES=5; // Steering dead cone around forward/backward axes
    const JOYSTICK_DEADZONE=0.12; // no movement within 12% of radius
    const JOYSTICK_MIN_OUTPUT=0.67; // 0.67 * 0.30 = 0.20 PWM at first movement
    let active=false,pointer=null,timer=null,x=0,y=0,busy=false;
    const card=document.getElementById("drive-card"),boost=document.createElement("button");
    boost.id="drive-turbo";boost.type="button";boost.textContent="×1";boost.style.fontSize="12px";boost.style.letterSpacing="-0.4px";boost.title="Motor speed multiplier";boost.setAttribute("aria-label","Motor speed multiplier ×1");const heading=card.querySelector(".drive-heading");heading.insertBefore(toggle,heading.firstChild);heading.append(boost);
    const levels=[100,150,200,300];let current=100,pending=false;
    function syncSpeed(value){
        const speed=Number(value);if(!Number.isFinite(speed))return;
        current=Math.max(100,Math.min(300,speed));boost.textContent=`×${current/100}`;
        boost.title=`Motor speed: ${current}%`;boost.setAttribute("aria-label",`Motor speed multiplier ×${current/100}`);
        boost.classList.toggle("active",current>100);
    }
    window.spySyncDriveSpeed=syncSpeed;
    boost.addEventListener("click",async()=>{
        if(pending)return;
        const index=levels.indexOf(current),next=levels[(index+1)%levels.length];pending=true;boost.disabled=true;
        try{
            const data=await (typeof adminPost==="function"?adminPost("/admin/motors/speed",{speed:next}):turtleRequest("/admin/motors/speed",{speed:next}));
            syncSpeed(data.speed);if(typeof driveSpeedSlider!=="undefined"&&driveSpeedSlider){driveSpeedSlider.value=data.speed;if(typeof showDriveSpeed==="function")showDriveSpeed(data.speed)}
        }catch(error){console.warn("[MOTOR SPEED]",error);if(typeof adminResult!=="undefined"&&adminResult)adminResult.textContent="Motor speed: "+error.message}
        finally{pending=false;boost.disabled=false}
    });
    if(typeof adminGet==="function")adminGet("/admin/motors/speed").then(data=>syncSpeed(data.speed)).catch(error=>console.warn("[MOTOR SPEED]",error));
    boost.addEventListener("contextmenu",e=>e.preventDefault());
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
    document.addEventListener("transportchange",()=>{release();if(typeof adminGet==="function")adminGet("/admin/motors/speed").then(data=>syncSpeed(data.speed)).catch(error=>console.warn("[MOTOR SPEED]",error))});
    render();
})();
