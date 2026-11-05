(() => {
    const language=document.getElementById("speech-language"),text=document.getElementById("speech-text"),button=document.getElementById("speech-say"),status=document.getElementById("speech-status");
    const modalLanguage=document.getElementById("message-language"),modalStatus=document.getElementById("message-status");
    if(!language||!modalLanguage)return;
    async function request(path,body){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth")throw Error("Ask and Speak require Wi-Fi (switch transport from Bluetooth)");
        let response;
        try{response=await fetch(path,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined,cache:"no-store"})}
        catch(error){throw Error(`Network error: ${error.message}`)}
        const raw=await response.text();let data;
        try{data=JSON.parse(raw)}catch{throw Error(`HTTP ${response.status}: ${raw.slice(0,200)||"Invalid server response"}`)}
        if(!response.ok){const detail=Array.isArray(data.detail)?JSON.stringify(data.detail):data.detail||data.message||"Unknown server error";throw Error(`${path} · HTTP ${response.status}: ${detail}`)}
        return data;
    }
    async function refresh(){try{const data=await request("/speech/settings");language.value=data.language;modalLanguage.value=data.language;status.textContent=data.voice_available?`Voice ready: ${data.voice}`:`Voice missing: ${data.voice}`}catch(error){status.textContent=error.message}}
    async function setLanguage(value){const data=await request("/speech/language",{language:value});language.value=data.language;modalLanguage.value=data.language;document.dispatchEvent(new CustomEvent("turtlelanguagechange",{detail:{language:data.language}}));return data}
    language.onchange=async()=>{try{const data=await setLanguage(language.value);status.textContent=`Language: ${data.language}`}catch(error){status.textContent=error.message;await refresh()}};
    modalLanguage.onchange=async()=>{try{await setLanguage(modalLanguage.value);modalStatus.textContent=""}catch(error){modalStatus.textContent=error.message;await refresh()}};
    async function act(path,content,target){target.textContent=path.includes("ask")?"Thinking...":"Generating speech...";const data=await request(path,content);target.textContent=data.answer?`Spy Turtle: ${data.answer}`:"Audio sent to speaker";return data}
    button.onclick=async()=>{button.disabled=true;try{await act("/speech/say",{text:text.value},status)}catch(error){status.textContent=error.message}finally{button.disabled=false}};
    const speak=document.getElementById("message-speak"),ask=document.getElementById("message-ask"),screen=document.getElementById("message-send-screen"),message=document.getElementById("message");
    async function submit(path){const value=message.value.trim();if(!value)return;const buttons=[speak,ask,screen];buttons.forEach(button=>button.disabled=true);try{await act(path,{text:value,language:modalLanguage.value},modalStatus)}catch(error){modalStatus.textContent=error.message;console.error("[SPY MESSAGE]",error)}finally{buttons.forEach(button=>button.disabled=false)}}
    speak.onclick=()=>submit("/speech/say");ask.onclick=()=>submit("/conversation/ask");
    document.addEventListener("transportchange",refresh);refresh();
})();
