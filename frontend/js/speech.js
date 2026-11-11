(() => {
    const modalLanguage=document.getElementById("message-language"),modalStatus=document.getElementById("message-status"),status=document.getElementById("speech-status");
    const groups={language:document.getElementById("speech-language-options"),en:document.getElementById("speech-voice-en"),fr:document.getElementById("speech-voice-fr")};
    // The language dropdown was removed from Bulle; the flags are authoritative.
    if(!groups.language)return;
    let selectedLanguage=document.querySelector('#message-language-buttons button[aria-pressed="true"]')?.dataset.lang||'fr';
    async function request(path,body){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth"){
            if(path==="/speech/say")return bluetoothAdminRequest("speech_say",body||{});
            if(path==="/conversation/ask"){
                const started=await bluetoothAdminRequest("chat_ask",body||{});
                const id=started.id,deadline=Date.now()+90000;
                while(Date.now()<deadline){
                    await new Promise(resolve=>setTimeout(resolve,1200));
                    if(transportMode!=="bluetooth")throw Error("Bluetooth disconnected");
                    const result=await bluetoothAdminRequest("chat_status");
                    if(result.id!==id)throw Error("Conversation replaced");
                    if(result.status==="error")throw Error(result.error||"Conversation failed");
                    if(result.status==="speaking"||result.status==="done")return {ok:true,answer:result.answer,queued:result.status!=="done"};
                }
                throw Error("Conversation still processing; check the robot");
            }
            throw Error("Speech settings require Wi-Fi");
        }
        const response=await fetch(path,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined,cache:"no-store"});
        const raw=await response.text();let data;
        try{data=JSON.parse(raw)}catch{throw Error(`HTTP ${response.status}: ${raw.slice(0,200)}`)}
        if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);
        return data;
    }
    function select(group,value,available){
        group?.querySelectorAll("button[data-value]").forEach(button=>{
            const active=button.dataset.value===value;button.classList.toggle("selected",active);button.setAttribute("aria-pressed",String(active));
            if(available){const installed=!!available[button.dataset.value];button.title=installed?"Piper model installed":"Piper model not installed yet";button.classList.toggle("voice-missing",!installed)}
        });
    }
    const pitch=document.getElementById("speech-pitch"),speed=document.getElementById("speech-speed"),pitchValue=document.getElementById("speech-pitch-value"),speedValue=document.getElementById("speech-speed-value");
    function displayTuning(){if(pitch&&pitchValue)pitchValue.textContent=`${Number(pitch.value)>0?"+":""}${pitch.value} st`;if(speed&&speedValue)speedValue.textContent=`${Number(speed.value).toFixed(2)}×`}
    async function saveTuning(){try{render(await request("/speech/tuning",{pitch:Number(pitch.value),speed:Number(speed.value)}))}catch(error){status.textContent=error.message;await refresh()}}
    for(const slider of [pitch,speed])if(slider){slider.addEventListener("input",displayTuning);slider.addEventListener("change",saveTuning)}
    function render(data){
        if(pitch&&data.pitch!==undefined)pitch.value=data.pitch;
        if(speed&&data.speed!==undefined)speed.value=data.speed;
        displayTuning();
        selectedLanguage=data.language;if(modalLanguage)modalLanguage.value=data.language;updateFlags();select(groups.language,data.language);select(groups.en,data.selected_voices?.en,data.available_voices?.en);select(groups.fr,data.selected_voices?.fr,data.available_voices?.fr);
        const active=data.selected_voices?.[data.language];status.textContent=data.voice_available?`Ready: ${active}`:`Model missing: ${data.voice}`;
    }
    async function refresh(){try{render(await request("/speech/settings"))}catch(error){status.textContent=error.message}}
    async function setLanguage(value){
        if(transportMode==="bluetooth"){
            selectedLanguage=value;updateFlags();document.dispatchEvent(new CustomEvent("turtlelanguagechange",{detail:{language:value}}));return {language:value};
        }
        const data=await request("/speech/language",{language:value});render(data);document.dispatchEvent(new CustomEvent("turtlelanguagechange",{detail:{language:data.language}}));return data;
    }
    groups.language.onclick=async event=>{const button=event.target.closest("button[data-value]");if(!button)return;try{await setLanguage(button.dataset.value)}catch(error){status.textContent=error.message;await refresh()}};
    for(const lang of ["en","fr"])groups[lang].onclick=async event=>{const button=event.target.closest("button[data-value]");if(!button)return;try{render(await request("/speech/voice",{language:lang,voice:button.dataset.value}))}catch(error){status.textContent=error.message;await refresh()}};
    const flagButtons=document.querySelectorAll("#message-language-buttons button[data-lang]");
    function updateFlags(){flagButtons.forEach(button=>{const selected=button.dataset.lang===selectedLanguage;button.classList.toggle("selected",selected);button.setAttribute("aria-pressed",String(selected))})}
    flagButtons.forEach(button=>button.addEventListener("click",async()=>{try{await setLanguage(button.dataset.lang);modalStatus.textContent="";updateFlags()}catch(error){modalStatus.textContent=error.message}}));
    document.addEventListener("turtlelanguagechange",updateFlags);updateFlags();
    if(modalLanguage)modalLanguage.onchange=async()=>{try{await setLanguage(modalLanguage.value);modalStatus.textContent=""}catch(error){modalStatus.textContent=error.message;await refresh()}};
    async function act(path,content,target){target.textContent=path.includes("ask")?"Thinking...":"Generating speech...";const data=await request(path,content);target.textContent=data.answer?`Spy Turtle: ${data.answer}`:data.queued?"Speech queued on Spy Turtle":"Audio sent to speaker";return data}
    const speak=document.getElementById("message-speak"),ask=document.getElementById("message-ask"),screen=document.getElementById("message-send-screen"),message=document.getElementById("message");
    async function submit(path){const value=message.value.trim();if(!value)return;const buttons=[speak,ask,screen].filter(Boolean);buttons.forEach(button=>button.disabled=true);try{await act(path,{text:value,language:selectedLanguage},modalStatus)}catch(error){modalStatus.textContent=error.message;console.error("[SPY MESSAGE]",error)}finally{buttons.forEach(button=>button.disabled=false)}}
    if(speak)speak.onclick=()=>submit("/speech/say");if(ask)ask.onclick=()=>submit("/conversation/ask");
    document.addEventListener("transportchange",()=>{if(transportMode==="wifi")refresh();else status.textContent="Bluetooth: speech and conversation available"});refresh();
})();
