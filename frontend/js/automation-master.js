(() => {
    const button=document.getElementById("automation-master"),admin=document.getElementById("automation-master-admin");
    const greet=document.getElementById("sentinel-enabled"),head=document.getElementById("automation-head"),sound=document.getElementById("automation-sounds"),movement=document.getElementById("automation-movement"),status=document.getElementById("automation-status");
    if(!button||!admin)return;
    const KEY="spy_turtle_automation_master",BACKUP="spy_turtle_automation_previous",SOUND="spy_turtle_automation_sounds";
    let enabled=localStorage.getItem(KEY)!=="false",idle=false,busy=false,previous=null;
    if(sound)sound.checked=localStorage.getItem(SOUND)!=="false";
    function errorMessage(error){if(status){status.hidden=false;status.textContent=error.message}console.error("[AUTOMATION]",error)}
    async function api(path,enabled){return turtleRequest(path,{enabled})}
    async function current(){
        const [s,m]=await Promise.all([turtleRequest("/sentinel/status"),turtleRequest("/brain/moods")]);
        return {greet:!!s.enabled,head:!!m.enable_head_movements};
    }
    function render(){
        button.classList.toggle("active",enabled&&!idle);button.disabled=busy||idle;button.setAttribute("aria-pressed",String(enabled&&!idle));
        admin.checked=enabled;admin.disabled=busy||idle;
        for(const c of [greet,head,sound])if(c)c.disabled=busy||idle||!enabled;
        if(movement)movement.disabled=true;
    }
    async function setBehaviors(value){await api("/sentinel/enable",value.greet);await api("/brain/head-movements",value.head);if(greet)greet.checked=value.greet;if(head)head.checked=value.head}
    async function apply(next){
        if(busy||idle||next===enabled)return;
        busy=true;render();
        try{
            if(!next){previous=await current();localStorage.setItem(BACKUP,JSON.stringify(previous));await setBehaviors({greet:false,head:false})}
            else{const saved=previous||JSON.parse(localStorage.getItem(BACKUP)||'{"greet":false,"head":false}');await setBehaviors(saved)}
            enabled=next;localStorage.setItem(KEY,String(enabled));if(status){status.textContent="";status.hidden=true}
        }catch(error){errorMessage(error)}finally{busy=false;render()}
    }
    async function onIdle(next){
        if(idle===next)return;
        idle=next;busy=true;render();
        try{
            if(next){if(enabled){previous=await current();await setBehaviors({greet:false,head:false})}}
            else if(enabled){await setBehaviors(previous||JSON.parse(localStorage.getItem(BACKUP)||'{"greet":false,"head":false}'))}
        }catch(error){errorMessage(error)}finally{busy=false;render()}
    }
    button.onclick=()=>apply(!enabled);admin.onchange=()=>apply(admin.checked);
    if(sound)sound.onchange=()=>localStorage.setItem(SOUND,String(sound.checked)); // Automation-only preference; does not change the general sound toggle.
    document.addEventListener("turtlepowerchange",event=>onIdle(!!event.detail.idle_mode));
    document.addEventListener("transportchange",render);
    render();
    if(!enabled){(async()=>{try{await setBehaviors({greet:false,head:false})}catch(error){errorMessage(error)}})()}
    // Automation sounds preference is separate from general sound. Backend event-level filtering is pending.
})();
