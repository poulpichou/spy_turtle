(() => {
    const grid=document.getElementById("commands-grid");if(!grid)return;
    const sections=[{name:"Moods",id:"moods",icon:"🐢"},{name:"Eyes",id:"faces",icon:"👀"},{name:"Shell LEDs",id:"leds",icon:"💡"},{name:"Back screen",id:"shell",icon:"🖥️"},{name:"Sounds",id:"audio",icon:"🔊"}];
    let version=0;
    const moodStyles=[['gassy','💨','gassy'],['dreamy','💭','dreamy'],['neutral','😐','neutral'],['happy','😊','happy'],['angry','😠','angry'],['sleep','😴','sleepy'],['curious','🤔','curious'],['surpris','😮','curious'],['sad','😢','sleepy'],['love','🥰','happy'],['scared','😨','sleepy'],['excited','🤩','happy']];
    const icons={status:'📊',log:'📜',rocket:'🚀',dance:'💃',smoke:'💨',fire:'🔥',sleep:'😴',leds:'💡',countdown:'⏳',loading:'⌛',glasses:'😎',glasses_large:'😎',happy:'😊',rocket_turtle:'🚀',walking:'🚶',off:'⚫',headlights:'🔦',neutral:'😐',rainbow:'🌈',breathing:'🫧',pulse:'💓',spinner:'🌀',wave:'🌊',police:'🚨',fart:'💨',cool:'😎',blink:'😉',surprised:'😮',angry:'😠',curious:'🤔',sad:'😢',yawn:'🥱'};
    function buttonStyle(section,item){
        const name=String(item.name||'').toLowerCase(),label=String(item.label||item.name||'');
        if(section==='moods'){
            const style=moodStyles.find(([key])=>name.includes(key));
            return {label:style?`${style[1]} ${label}`:label,tone:style?.[2]||''};
        }
        const key=name.split('_')[0];return {label:icons[name]||icons[key]?`${icons[name]||icons[key]} ${label}`:label,tone:''};
    }
    async function items(id){
        if(transportMode!=="bluetooth"){
            if(id==="moods"){const data=await turtleRequest("/brain/moods");return (data.variants||[]).map(x=>({name:x.id,label:x.id.replaceAll("_"," ")}))}
            const assets=await getAssets();return assets[id]||[];
        }
        const result=[];
        for(let offset=0;offset<150;){
            const data=await bluetoothAdminRequest(id==="moods"?"mood_list":"asset_list",id==="moods"?{offset}:{section:id,offset});
            const batch=id==="moods"?(data.variants||[]).map(x=>({name:x.id,label:x.id.replaceAll("_"," ")})):(data.items||[]);
            result.push(...batch);offset+=batch.length;
            if(!batch.length||offset>=data.total)break;
        }
        return result;
    }
    async function render(){
        const request=++version;grid.replaceChildren();
        for(const section of sections){
            if(request!==version)return;
            const card=document.createElement("section");card.className="commands-category";
            const title=document.createElement("h3");title.textContent=`${section.icon} ${section.name}`;
            const buttons=document.createElement("div");buttons.className="commands-buttons";card.append(title,buttons);grid.append(card);
            try{
                const entries=await items(section.id);if(request!==version)return;
                if(section.id==="shell")entries.unshift({name:"status",label:"Status"},{name:"log",label:"Log"});
                for(const item of entries){
                    const button=document.createElement("button");const style=buttonStyle(section.id,item);button.textContent=style.label;button.title=item.label||item.name;if(style.tone)button.dataset.moodTone=style.tone;
                    button.onclick=async()=>{button.disabled=true;try{if(section.id==="moods")await turtleRequest("/brain/moods/select",{variant:item.name});else await sendCommand({faces:"face",leds:"led",shell:"shell",audio:"sound"}[section.id],item.name)}catch(error){alert(error.message)}finally{button.disabled=false}};
                    buttons.append(button);
                }
            }catch(error){const message=document.createElement("span");message.className="commands-error";message.textContent=error.message;buttons.append(message)}
        }
    }
    document.addEventListener("transportchange",()=>{if(document.querySelector('.center-tab.active')?.dataset.view==="commands")render()});
    document.querySelector('[data-view="commands"]')?.addEventListener("click",render);
})();
