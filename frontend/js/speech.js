(() => {
    const modalLanguage=document.getElementById("message-language"),modalStatus=document.getElementById("message-status"),status=document.getElementById("speech-status");
    const groups={language:document.getElementById("speech-language-options"),en:document.getElementById("speech-voice-en"),fr:document.getElementById("speech-voice-fr")};
    if(!modalLanguage||!groups.language)return;
    async function request(path,body){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth")throw Error("Speech settings require Wi-Fi");
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
    function render(data){
        modalLanguage.value=data.language;select(groups.language,data.language);select(groups.en,data.selected_voices?.en,data.available_voices?.en);select(groups.fr,data.selected_voices?.fr,data.available_voices?.fr);
        const active=data.selected_voices?.[data.language];status.textContent=data.voice_available?`Ready: ${active}`:`Model missing: ${data.voice}`;
    }
    async function refresh(){try{render(await request("/speech/settings"))}catch(error){status.textContent=error.message}}
    async function setLanguage(value){const data=await request("/speech/language",{language:value});render(data);document.dispatchEvent(new CustomEvent("turtlelanguagechange",{detail:{language:data.language}}));return data}
    groups.language.onclick=async event=>{const button=event.target.closest("button[data-value]");if(!button)return;try{await setLanguage(button.dataset.value)}catch(error){status.textContent=error.message;await refresh()}};
    for(const lang of ["en","fr"])groups[lang].onclick=async event=>{const button=event.target.closest("button[data-value]");if(!button)return;try{render(await request("/speech/voice",{language:lang,voice:button.dataset.value}))}catch(error){status.textContent=error.message;await refresh()}};
    modalLanguage.onchange=async()=>{try{await setLanguage(modalLanguage.value);modalStatus.textContent=""}catch(error){modalStatus.textContent=error.message;await refresh()}};
    async function act(path,content,target){target.textContent=path.includes("ask")?"Thinking...":"Generating speech...";const data=await request(path,content);target.textContent=data.answer?`Spy Turtle: ${data.answer}`:"Audio sent to speaker";return data}
    const speak=document.getElementById("message-speak"),ask=document.getElementById("message-ask"),screen=document.getElementById("message-send-screen"),message=document.getElementById("message");
    async function submit(path){const value=message.value.trim();if(!value)return;const buttons=[speak,ask,screen].filter(Boolean);buttons.forEach(button=>button.disabled=true);try{await act(path,{text:value,language:modalLanguage.value},modalStatus)}catch(error){modalStatus.textContent=error.message;console.error("[SPY MESSAGE]",error)}finally{buttons.forEach(button=>button.disabled=false)}}
    if(speak)speak.onclick=()=>submit("/speech/say");if(ask)ask.onclick=()=>submit("/conversation/ask");
    document.addEventListener("transportchange",refresh);refresh();
})();
