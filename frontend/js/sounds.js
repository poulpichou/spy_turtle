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
    }catch(error){
        console.error("[SOUNDS] unable to load catalog",error);
    }
}
loadSoundCatalog();
