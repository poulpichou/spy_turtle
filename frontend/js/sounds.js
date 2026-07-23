let soundSelectInitialized=false;

async function playSelectedSound(event){
    const select=event.currentTarget;
    const sound=select.value;
    if(!sound)return;
    try{
        await sendCommand("sound",sound);
        console.log("[SOUNDS] played",sound);
    }catch(error){
        showCommandError(error);
    }finally{
        select.selectedIndex=0;
    }
}

async function loadSoundCatalog(){
    const select=document.getElementById("sound-select");
    if(!select)return;
    try{
        const assets=await getAssets();
        const sounds=assets.audio||[];
        select.innerHTML='<option value="" selected disabled>Choose sound...</option>';
        sounds.forEach(sound=>{
            const option=document.createElement("option");
            option.value=sound.name;
            option.textContent=sound.label||sound.name;
            select.appendChild(option);
        });
        if(!soundSelectInitialized){
            select.addEventListener("change",playSelectedSound);
            soundSelectInitialized=true;
        }
    }catch(error){
        console.error("[SOUNDS] unable to load catalog",error);
    }
}

loadSoundCatalog();
