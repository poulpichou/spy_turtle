(() => {
    const language=document.getElementById("speech-language"),text=document.getElementById("speech-text"),button=document.getElementById("speech-say"),status=document.getElementById("speech-status");
    if(!language||!text||!button||!status)return;
    async function request(path,body){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth")throw Error("Speech setup currently requires Wi-Fi");
        const response=await fetch(path,{method:body?"POST":"GET",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined,cache:"no-store"});
        const data=await response.json();if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);return data;
    }
    async function refresh(){try{const data=await request("/speech/settings");language.value=data.language;status.textContent=data.voice_available?`Voice ready: ${data.voice}`:`Voice missing: ${data.voice}`}catch(error){status.textContent=error.message}}
    language.onchange=async()=>{try{const data=await request("/speech/language",{language:language.value});status.textContent=`Language: ${data.language}${data.voice_available?"":" (voice not installed)"}`}catch(error){status.textContent=error.message;await refresh()}};
    button.onclick=async()=>{button.disabled=true;status.textContent="Generating speech...";try{await request("/speech/say",{text:text.value});status.textContent="Audio sent to speaker"}catch(error){status.textContent=error.message}finally{button.disabled=false}};
    document.addEventListener("transportchange",refresh);refresh();
})();
