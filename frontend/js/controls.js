function startMove(direction){sendCommand("move",direction).catch(showCommandError)}
function stopMove(){sendCommand("move","stop").catch(showCommandError)}
function showCommandError(error){console.error(error);alert(error.message)}
function setupMovementButton(id,direction){const button=document.getElementById(id);button.addEventListener("mousedown",()=>startMove(direction));button.addEventListener("mouseup",stopMove);button.addEventListener("mouseleave",stopMove);button.addEventListener("touchstart",event=>{event.preventDefault();startMove(direction)},{passive:false});button.addEventListener("touchend",event=>{event.preventDefault();stopMove()},{passive:false});button.addEventListener("touchcancel",stopMove)}
setupMovementButton("forward","forward");setupMovementButton("backward","backward");setupMovementButton("left","left");setupMovementButton("right","right");document.getElementById("stop").onclick=stopMove;
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
    hello:{face:"happy",shell:"happy",led:"wave"},
    happy:{face:"happy",shell:"happy",led:"breathing"},
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
function closeMessageEditor(){messageModal.hidden=true;messageInput.value=""}
async function sendMessage(){const message=messageInput.value.trim();if(!message)return;try{await sendCommand("shell_text",message);closeMessageEditor()}catch(error){showCommandError(error)}}
document.getElementById("screen-message-button").onclick=openMessageEditor;
document.getElementById("message-close").onclick=closeMessageEditor;
messageModal.addEventListener("click",event=>{if(event.target===messageModal)closeMessageEditor()});
messageInput.addEventListener("keydown",event=>{if(event.key==="Enter"&&!event.shiftKey){event.preventDefault();sendMessage()}else if(event.key==="Escape"){event.preventDefault();closeMessageEditor()}});
