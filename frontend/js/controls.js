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

const animations={
    hello:{face:"happy",shell:"turtle_happy",led:"wave"},
    happy:{face:"happy",shell:"turtle_happy",led:"breathing"},
    party:{face:"happy",shell:"dance",led:"dance"},
    rocket:{face:"surprised",shell:"rocket",led:"rocket"},
    sleep:{face:"sleeping",shell:"sleep",led:"off"},
    fart:{face:"surprised",shell:"smoke",led:"fart",sound:"fart1"}
};
async function playAnimation(name){
    const animation=animations[name];if(!animation)return;
    const commands=[["face",animation.face],["shell",animation.shell],["led",animation.led]];
    if(animation.sound)commands.push(["sound",animation.sound]);
    await Promise.all(commands.map(([type,value])=>sendCommand(type,value)));
}
document.getElementById("animation-select").onchange=event=>{if(event.target.value)playAnimation(event.target.value).catch(showCommandError)};

const messageModal=document.getElementById("message-modal"),messageInput=document.getElementById("message");
function openMessageEditor(){messageModal.hidden=false;messageInput.focus()}
function closeMessageEditor(){messageModal.hidden=true;document.getElementById("message-status").textContent=""}
async function sendMessage(){const message=messageInput.value.trim();if(!message)return;try{await sendCommand("shell_text",message);document.getElementById("message-status").textContent="Sent to screen"}catch(error){showCommandError(error)}}
document.getElementById("screen-message-button").onclick=openMessageEditor;
document.getElementById("message-close").onclick=closeMessageEditor;
document.getElementById("message-send-screen").onclick=sendMessage;
messageModal.addEventListener("click",event=>{if(event.target===messageModal)closeMessageEditor()});
messageInput.addEventListener("keydown",event=>{if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();sendMessage()}else if(event.key==="Escape"){event.preventDefault();closeMessageEditor()}});
