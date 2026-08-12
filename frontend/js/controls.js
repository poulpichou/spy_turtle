function startMove(direction){sendCommand("move",direction).catch(showCommandError)}function stopMove(){sendCommand("move","stop").catch(showCommandError)}function showCommandError(error){console.error(error);alert(error.message)}function setupMovementButton(id,direction){const button=document.getElementById(id);button.addEventListener("mousedown",()=>startMove(direction));button.addEventListener("mouseup",stopMove);button.addEventListener("mouseleave",stopMove);button.addEventListener("touchstart",event=>{event.preventDefault();startMove(direction)},{passive:false});button.addEventListener("touchend",event=>{event.preventDefault();stopMove()},{passive:false});button.addEventListener("touchcancel",stopMove)}setupMovementButton("forward","forward");setupMovementButton("backward","backward");setupMovementButton("left","left");setupMovementButton("right","right");document.getElementById("stop").onclick=stopMove;function setupHeadButton(id,direction){document.getElementById(id).onclick=()=>sendCommand("head",direction).catch(showCommandError)}setupHeadButton("head-left","left");setupHeadButton("head-right","right");setupHeadButton("head-up","up");setupHeadButton("head-down","down");setupHeadButton("head-center","center");document.getElementById("face-select").onchange=event=>sendCommand("face",event.target.value).catch(showCommandError);document.getElementById("shell-select").onchange=event=>sendCommand("shell",event.target.value).catch(showCommandError);document.getElementById("led-select").onchange=event=>sendCommand("led",event.target.value).catch(showCommandError);

const soundSelect=document.getElementById("sound-select");soundSelect.onchange=event=>{if(event.target.value)sendCommand("sound",event.target.value).catch(showCommandError)};
async function loadSounds(){try{const data=await getAssets(),sounds=data.audio||[];soundSelect.replaceChildren();for(const sound of sounds){const option=document.createElement("option");option.value=sound.name;option.textContent=sound.label||sound.name;soundSelect.appendChild(option)}if(!sounds.length){const option=document.createElement("option");option.textContent="No sounds";option.value="";soundSelect.appendChild(option)}}catch(error){console.error("[SOUNDS]",error)}}loadSounds();

const animations={
    hello:{face:"happy",shell:"happy",led:"wave",sound:"applause"},
    happy:{face:"happy",shell:"happy",led:"breathing",sound:"laugh"},
    party:{face:"happy",shell:"dance",led:"dance",sound:"applause"},
    rocket:{face:"surprised",shell:"rocket",led:"rocket",sound:"rocket"},
    sleep:{face:"sleeping",shell:"sleep",led:"off",sound:""},
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
