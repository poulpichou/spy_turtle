(() => {
    const picker=document.getElementById("headlight-color-picker"),label=document.getElementById("headlight-color-value"),presets=document.getElementById("headlight-presets");
    const setColor=value=>{picker.value=value;label.textContent=""};
    async function saveColor(value){
        if(typeof transportMode!=="undefined"&&transportMode==="bluetooth")throw Error("Headlights color requires Wi-Fi");
        const response=await fetch("/admin/leds/headlights/color",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({color:value})});
        const data=await response.json();if(!response.ok)throw Error(data.detail||"Unable to save color");setColor(data.color);
    }
    if(picker){
        fetch("/admin/leds/headlights/color",{cache:"no-store"}).then(r=>r.ok?r.json():null).then(d=>{if(d?.color)setColor(d.color)}).catch(()=>{});
        picker.addEventListener("input",()=>setColor(picker.value));
        picker.addEventListener("change",()=>saveColor(picker.value).catch(e=>alert(e.message)));
        presets?.addEventListener("click",event=>{const b=event.target.closest("button[data-color]");if(b)saveColor(b.dataset.color).catch(e=>alert(e.message))});
    }
    const reset=document.getElementById("message-reset");if(reset)reset.onclick=()=>{const m=document.getElementById("message");m.value="";m.dispatchEvent(new Event("input",{bubbles:true}));m.focus()};
    const button=document.getElementById("message-dictate"),message=document.getElementById("message"),status=document.getElementById("message-status");
    const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!button||!message)return;
    if(!Recognition){button.disabled=true;button.title="Phone speech recognition unavailable in this browser";return}
    let recognition=null;
    button.onclick=()=>{
        if(recognition){recognition.stop();return}
        recognition=new Recognition();recognition.lang=(document.getElementById("message-language")?.value||"fr")==="en"?"en-US":"fr-FR";
        recognition.continuous=false;recognition.interimResults=false;
        recognition.onresult=event=>{
            const spoken=Array.from(event.results).map(result=>result[0]?.transcript||"").join(" ").trim();
            if(spoken){message.value=[message.value.trim(),spoken].filter(Boolean).join(" ");message.dispatchEvent(new Event("input",{bubbles:true}))}
            status.textContent=spoken?"Dictation added. Review before sending.":"No speech recognized";
        };
        recognition.onerror=event=>{status.textContent=`Dictation: ${event.error}`};
        recognition.onend=()=>{recognition=null;button.textContent="🎤"};
        try{recognition.start();button.textContent="⏹";status.textContent="Listening on phone..."}
        catch(error){recognition=null;button.textContent="🎤";status.textContent=error.message}
    };
})();
