(() => {
    const button=document.getElementById("automation-master"),admin=document.getElementById("automation-master-admin");
    const greet=document.getElementById("sentinel-enabled"),head=document.getElementById("automation-head"),sound=document.getElementById("automation-sounds"),movement=document.getElementById("automation-movement");
    if(!button||!admin)return;
    const KEY="spy_turtle_automation_master",BACKUP="spy_turtle_automation_previous";
    let enabled=localStorage.getItem(KEY)!=="false",busy=false;
    const status=document.getElementById("automation-status");
    function showError(error){if(status){status.hidden=false;status.textContent=error.message}console.error("[AUTOMATION]",error)}
    async function api(path,enabled){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth")throw Error("Automation settings require Wi-Fi");
        const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({enabled}),cache:"no-store"});
        const result=await response.json();if(!response.ok)throw Error(result.detail||`HTTP ${response.status}`);return result;
    }
    async function current(){
        const get=async path=>{const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error(`${path}: HTTP ${r.status}`);return r.json()};
        const [s,m]=await Promise.all([get("/sentinel/status"),get("/brain/moods")]);
        return {greet:!!s.enabled,head:!!m.enable_head_movements,sound:localStorage.getItem("spy_turtle_sound_enabled")!=="false"};
    }
    function render(){
        button.classList.toggle("active",enabled);button.setAttribute("aria-pressed",String(enabled));button.disabled=busy;
        admin.checked=enabled;admin.disabled=busy;
        for(const control of [greet,head,sound])if(control)control.disabled=busy||!enabled;
        if(movement)movement.disabled=true; // Autonomous driving is not implemented.
    }
    async function setSound(value){
        const toggle=document.getElementById("sound-toggle");
        const active=localStorage.getItem("spy_turtle_sound_enabled")!=="false";
        if(active!==value&&toggle)toggle.click();
        if(sound)sound.checked=value;
    }
    async function apply(next){
        if(busy||next===enabled)return;
        busy=true;render();
        try{
            const previous=next?JSON.parse(localStorage.getItem(BACKUP)||'{"greet":false,"head":false,"sound":true}'):await current();
            if(!next)localStorage.setItem(BACKUP,JSON.stringify(previous));
            const desired=next?previous:{greet:false,head:false,sound:false};
            await api("/sentinel/enable",desired.greet);
            await api("/brain/head-movements",desired.head);
            await setSound(desired.sound);
            if(greet)greet.checked=desired.greet;
            if(head)head.checked=desired.head;
            enabled=next;localStorage.setItem(KEY,String(enabled));
            if(status){status.textContent="";status.hidden=true}
        }catch(error){showError(error)}
        finally{busy=false;render()}
    }
    button.onclick=()=>apply(!enabled);
    admin.onchange=()=>apply(admin.checked);
    render();
    // The master switch controls Sentinel, head motion and the existing frontend sound toggle.
    // Its state is per browser; it does not disable face recognition or autonomous driving.
    if(!enabled){
        (async()=>{try{await api("/sentinel/enable",false);await api("/brain/head-movements",false);await setSound(false);if(greet)greet.checked=false;if(head)head.checked=false}catch(error){showError(error)}finally{render()}})();
    }
    document.addEventListener("transportchange",()=>{render()});
})();
