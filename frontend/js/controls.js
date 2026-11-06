let heldDirection=null,heldTimer=null;
function showCommandError(error){console.error(error);if(heldDirection)releaseMovement();else alert(error.message)}
function releaseMovement(){
    heldDirection=null;
    if(heldTimer){clearInterval(heldTimer);heldTimer=null}
    sendCommand("move","stop").catch(error=>console.warn("[SAFETY] Stop not delivered; robot watchdog will stop motors",error));
}
function startMove(direction){
    if(heldDirection===direction)return;
    if(heldDirection)releaseMovement();
    heldDirection=direction;
    const tick=()=>{
        if(heldDirection!==direction)return;
        if(transportMode==="bluetooth"&&bluetoothPending>1)return;
        sendCommand("move",direction).catch(error=>{console.warn("[SAFETY] Movement failed",error);releaseMovement()});
    };
    tick();heldTimer=setInterval(tick,350);
}
function stopMove(){releaseMovement()}
function setupMovementButton(id,direction){
    const button=document.getElementById(id);
    button.addEventListener("contextmenu",event=>event.preventDefault());
    button.addEventListener("pointerdown",event=>{event.preventDefault();button.setPointerCapture(event.pointerId);startMove(direction)});
    button.addEventListener("pointerup",stopMove);
    button.addEventListener("pointercancel",stopMove);
    button.addEventListener("lostpointercapture",()=>{if(heldDirection===direction)stopMove()});
}
setupMovementButton("forward","forward");setupMovementButton("backward","backward");setupMovementButton("left","left");setupMovementButton("right","right");
document.getElementById("stop").onclick=stopMove;
window.addEventListener("blur",()=>{if(heldDirection)releaseMovement()});
document.addEventListener("visibilitychange",()=>{if(document.hidden&&heldDirection)releaseMovement()});
document.addEventListener("transportchange",()=>{if(heldDirection)releaseMovement()});
function setupHeadButton(id,direction){document.getElementById(id).onclick=()=>sendCommand("head",direction).catch(showCommandError)}
setupHeadButton("head-left","left");setupHeadButton("head-right","right");setupHeadButton("head-up","up");setupHeadButton("head-down","down");setupHeadButton("head-center","center");

const assetSelects={faces:document.getElementById("face-select"),shell:document.getElementById("shell-select"),leds:document.getElementById("led-select"),audio:document.getElementById("sound-select")};
assetSelects.faces.onchange=event=>sendCommand("face",event.target.value).catch(showCommandError);
assetSelects.shell.onchange=event=>sendCommand("shell",event.target.value).catch(showCommandError);
assetSelects.leds.onchange=event=>sendCommand("led",event.target.value).catch(showCommandError);
assetSelects.audio.onchange=event=>{if(event.target.value)sendCommand("sound",event.target.value).catch(showCommandError)};

function assetOption(name,label){const option=document.createElement("option");option.value=name;option.textContent=label||name;return option}
function fillAssetSelect(select,items,prefix=[]){
    const previous=select.value;select.replaceChildren();
    for(const item of prefix)select.appendChild(assetOption(item.name,item.label));
    for(const item of items||[])select.appendChild(assetOption(item.name,item.label));
    if([...select.options].some(option=>option.value===previous))select.value=previous;
}
async function loadAssetControls(){
    try{
        const data=await getAssets();
        fillAssetSelect(assetSelects.faces,data.faces);
        fillAssetSelect(assetSelects.shell,data.shell,[{name:"status",label:"Status"},{name:"log",label:"Log"}]);
        fillAssetSelect(assetSelects.leds,data.leds);
        fillAssetSelect(assetSelects.audio,data.audio,[{name:"",label:"Choose sound..."}]);
    }catch(error){console.error("[ASSETS]",error)}
}
loadAssetControls();

async function loadMoodControls(){
    const select=document.getElementById("animation-select");
    try{
        const response=await fetch("/brain/moods",{cache:"no-store"});if(!response.ok)throw Error(`HTTP ${response.status}`);
        const data=await response.json(),entries=data.variants||data.moods||[];
        const moods=entries.map(item=>typeof item==="string"?{id:item,mood:item}:item);
        select.replaceChildren(assetOption("","Choose mood..."));
        for(const mood of moods)select.appendChild(assetOption(mood.id||mood.mood,mood.label||mood.mood||mood.id));
        if(!moods.length){select.replaceChildren(assetOption("","Mood API unavailable"));select.disabled=true}
    }catch(error){select.replaceChildren(assetOption("","Mood API unavailable"));select.disabled=true;console.warn("[MOODS]",error)}
}
document.getElementById("animation-select").onchange=async event=>{
    if(!event.target.value)return;
    try{const response=await fetch("/brain/moods/select",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({variant:event.target.value})});if(!response.ok)throw Error((await response.text()).slice(0,200))}
    catch(error){showCommandError(error)}
};
loadMoodControls();

const messageModal=document.getElementById("message-modal"),messageInput=document.getElementById("message");
function openMessageEditor(){messageModal.hidden=false;messageInput.focus()}
function closeMessageEditor(){messageModal.hidden=true;document.getElementById("message-status").textContent=""}
async function sendMessage(){const message=messageInput.value.trim();if(!message)return;try{await sendCommand("shell_text",message);document.getElementById("message-status").textContent="Sent to screen"}catch(error){showCommandError(error)}}
document.getElementById("screen-message-button").onclick=openMessageEditor;

document.getElementById("message-send-screen").onclick=sendMessage;
messageModal.addEventListener("click",event=>{if(event.target===messageModal)closeMessageEditor()});
messageInput.addEventListener("keydown",event=>{if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();sendMessage()}else if(event.key==="Escape"){event.preventDefault();closeMessageEditor()}});
