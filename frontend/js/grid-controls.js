/* Spy Turtle compact 3x2 control grids. Preserves existing controls and handlers. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const left=$('left-panel'),right=$('right-panel'),idle=$('idle-toggle');
if(!left||!right||!idle||$('spy-left-grid'))return;
const grid=(id,parent,before)=>{const e=document.createElement('div');e.id=id;e.className='spy-control-grid';parent.insertBefore(e,before);return e};
const leftGrid=grid('spy-left-grid',left,left.querySelector('.idle-lights-row'));
const rightGrid=grid('spy-right-grid',right,right.querySelector('.right-control'));
function tile(name,icon,handler,options={}){
 const box=document.createElement('div');box.className='spy-tile';box.dataset.name=name;
 const main=document.createElement('button');main.type='button';main.className='spy-tile-main';main.textContent=icon;main.title=name;main.setAttribute('aria-label',name);main.onclick=handler;
 box.append(main);
 if(options.menu){const arrow=document.createElement('button');arrow.type='button';arrow.className='spy-tile-arrow';arrow.textContent='⌄';arrow.title='Choose '+name;arrow.setAttribute('aria-label','Choose '+name);arrow.onclick=options.menu;box.append(arrow)}
 return {box,main};
}
function relocate(id,grid,icon){
 const button=$(id),card=button?.closest('.card');if(!button||!card)return;
 card.classList.add('spy-tile','spy-existing-tile');card.dataset.name=id;
 const line=button.closest('.control-line');if(line)line.classList.add('spy-tile-line');
 button.classList.add('spy-tile-main');if(icon)button.textContent=icon;
 const picker=line?.querySelector('.compact-select');if(picker){picker.classList.add('spy-tile-picker');const arrow=picker.querySelector('.compact-select-button');if(arrow){arrow.textContent='⌄';arrow.title='Choose '+id;arrow.setAttribute('aria-label','Choose '+id)}}
 grid.append(card);
}
function relocateButton(id,grid,icon){
 const button=$(id);if(!button)return;
 const box=document.createElement('div');box.className='spy-tile spy-toggle-tile';box.dataset.name=id;
 button.classList.add('spy-tile-main');
 if(icon){const label=button.querySelector('span');if(label){for(const node of [...button.childNodes])if(node!==label)node.remove();button.insertBefore(document.createTextNode(icon+' '),label)}else button.textContent=icon}
 box.append(button);grid.append(box);return box;
}
function popup(title,items,anchor){
 document.querySelector('.spy-grid-popover')?.remove();
 const panel=document.createElement('div');panel.className='spy-grid-popover';panel.setAttribute('role','dialog');panel.setAttribute('aria-label',title);
 const heading=document.createElement('strong');heading.textContent=title;panel.append(heading);
 for(const item of items){const b=document.createElement('button');b.type='button';b.textContent=item.label;if(title==='Language')b.dataset.spyLanguage='true';if(title==='System actions')b.dataset.spySystemAction='true';b.onclick=()=>{panel.remove();item.run()};panel.append(b)}
 document.body.append(panel);
 const rect=anchor.getBoundingClientRect(),pw=panel.getBoundingClientRect().width,ph=panel.getBoundingClientRect().height;
 panel.style.left=Math.max(5,Math.min(innerWidth-pw-5,rect.left))+'px';
 panel.style.top=(rect.bottom+ph+5<innerHeight?rect.bottom+4:Math.max(5,rect.top-ph-4))+'px';
 const close=e=>{if(!panel.contains(e.target)&&!anchor.contains(e.target)){panel.remove();document.removeEventListener('pointerdown',close,true)}};
 setTimeout(()=>document.addEventListener('pointerdown',close,true),0);
}
function choose(name,items){return event=>popup(name,items,event.currentTarget)}
function clickAdmin(action){const button=document.querySelector(`[data-admin-action="${action}"]`);if(button)button.click()}
const power=tile('Power','🛠️',()=>clickAdmin('reset'),{menu:event=>popup('System actions',[
 {label:'🔄 Restart Turtle',run:()=>clickAdmin('restart')},{label:'🔁 Reboot Pi',run:()=>clickAdmin('reboot')},{label:'🛑 Shutdown Pi',run:()=>clickAdmin('shutdown')}
],event.currentTarget)});
relocateButton('idle-toggle',leftGrid,'🌙');power.box.classList.add('spy-system-tile');leftGrid.append(power.box);
const originalView=$('turtle-view-toggle');
if(originalView){originalView.classList.add('spy-legacy-hidden');originalView.parentElement?.classList.add('spy-legacy-row')}
let vision=localStorage.getItem('spy_grid_vision_mode')||'robot';
const visionTile=document.createElement('div');visionTile.className='spy-tile spy-vision-segment';visionTile.dataset.name='Vision';
const visionButtons={};
for(const [mode,icon,label] of [['turtle','🐢','Turtle view'],['robot','🤖','Robot view'],['thermal','🌡️','Thermal view']]){
 const b=document.createElement('button');b.type='button';b.textContent=icon;b.title=label;b.setAttribute('aria-label',label);b.onclick=()=>setVision(mode);visionTile.append(b);visionButtons[mode]=b;
}
function setVision(mode){
 vision=mode;localStorage.setItem('spy_grid_vision_mode',mode);
 if(mode!=='thermal'){
  const active=!!window.spyTurtleImageEffects?.isEnabled();
  if(active!==(mode==='turtle'))originalView?.click();
  document.querySelector('[data-view="camera"]')?.click();
 }else{
  if(window.spyTurtleImageEffects?.isEnabled())originalView?.click();
  document.querySelector('[data-view="camera"]')?.click();
 }
 window.spySetThermalVision?.(mode==='thermal');
 syncVision();
}
function syncVision(){
 const active=!!window.spyTurtleImageEffects?.isEnabled();
 if(vision!=='thermal')vision=active?'turtle':'robot';
 for(const [mode,b] of Object.entries(visionButtons)){b.classList.toggle('selected',mode===vision);b.setAttribute('aria-pressed',String(mode===vision))}
}
leftGrid.append(visionTile);
relocateButton('automation-master',leftGrid,'🦾');
let chatbot=false;
const chat=tile('Chatbot','🗣️',()=>{chatbot=!chatbot;syncChat()}, {menu:event=>popup('Language',[
 {label:'🇫🇷',run:()=>setLanguage('fr')},{label:'🇬🇧',run:()=>setLanguage('en')}
],event.currentTarget)});
function syncChat(){chat.box.classList.toggle('selected',chatbot);chat.main.setAttribute('aria-pressed',String(chatbot));chat.main.title=chatbot?'Chatbot ON (UI placeholder)':'Chatbot OFF (UI placeholder)'}
function setLanguage(lang){
 document.querySelector(`#speech-language-options [data-value="${lang}"]`)?.click();
 document.querySelector(`#message-language-buttons [data-lang="${lang}"]`)?.click();
 localStorage.setItem('spy_grid_language',lang);
 chat.box.dataset.lang=lang;chat.box.querySelector('.spy-tile-arrow').title=lang==='en'?'Chatbot language: English':'Chatbot language: French';
}
chat.box.classList.add('spy-chat-tile');syncChat();leftGrid.append(chat.box);
setLanguage(document.querySelector('#speech-language-options .selected')?.dataset.value||localStorage.getItem('spy_grid_language')||'fr');
relocate('animation-toggle',rightGrid,'🎭');
const headlightStash=document.createElement('div');headlightStash.id='spy-headlight-stash';headlightStash.hidden=true;document.body.append(headlightStash);
for(const id of ['headlight-color-control','headlight-intensity-slider']){
 const el=$(id),wrapper=id==='headlight-intensity-slider'?el?.closest('.admin-slider'):el;
 if(wrapper)headlightStash.append(wrapper);
}
const light=relocateButton('headlights-toggle',rightGrid,'💡');
if(light){
 const arrow=document.createElement('button');arrow.type='button';arrow.className='spy-tile-arrow';arrow.textContent='⌄';arrow.title='Headlight colors';arrow.onclick=()=>{
  const presets=$('headlight-presets'),picker=$('headlight-color-picker'),items=[...presets?.querySelectorAll('[data-color]')||[]];
  const overlay=document.createElement('div');overlay.className='spy-grid-modal';overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');
  const panel=document.createElement('div');panel.className='spy-grid-modal-panel';const heading=document.createElement('div');heading.className='spy-grid-modal-heading';heading.textContent='💡 Headlight color';
  const intensityRow=$('headlight-intensity-slider')?.closest('.admin-slider');
  const dismiss=()=>{if(intensityRow)headlightStash.append(intensityRow);overlay.remove()};
  const close=document.createElement('button');close.type='button';close.textContent='×';close.onclick=dismiss;heading.append(close);panel.append(heading);
  const colors=document.createElement('div');colors.className='spy-grid-colors';
  for(const item of items){const b=document.createElement('button');b.type='button';b.title=item.title||item.dataset.color;b.style.background=item.dataset.color;b.setAttribute('aria-label',b.title);b.onclick=()=>{item.click();dismiss()};colors.append(b)}
  const custom=document.createElement('button');custom.type='button';custom.textContent='🎨 Custom';custom.onclick=()=>picker?.click();
  panel.append(colors,custom);if(intensityRow)panel.append(intensityRow);overlay.append(panel);overlay.onclick=e=>{if(e.target===overlay)dismiss()};document.body.append(overlay);
 };light.append(arrow);
}
relocate('sound-toggle',rightGrid,'🔊');
relocate('eyes-toggle',rightGrid,'👀');
relocate('shell-light-toggle',rightGrid,'✨');
relocate('back-screen-toggle',rightGrid,'▭');
document.querySelector('.idle-lights-row')?.classList.add('spy-legacy-hidden');
function syncIdle(){document.body.classList.toggle('spy-grid-idle',idle.classList.contains('active')||idle.getAttribute('aria-pressed')==='true')}
document.addEventListener('turtlepowerchange',event=>{document.body.classList.toggle('spy-grid-idle',!!event.detail?.idle_mode);if(event.detail?.idle_mode){chatbot=false;syncChat()}});
document.addEventListener('click',event=>{if(event.target===originalView||event.target?.dataset?.view)queueMicrotask(syncVision)});
const observer=new MutationObserver(()=>{syncIdle();syncVision()});
observer.observe(idle,{attributes:true,attributeFilter:['class','aria-pressed']});
if(originalView)observer.observe(originalView,{attributes:true,attributeFilter:['class','aria-pressed']});
// Shared visual state for all toggles, including left-side Automation and Idle.
function setGridVisual(button,on){
 if(!button)return;
 button.dataset.gridVisualState=on?'on':'off';
 const tile=button.closest('.spy-tile');if(tile)tile.dataset.gridVisualState=on?'on':'off';
}
for(const id of ['animation-toggle','sound-toggle','eyes-toggle','back-screen-toggle','shell-light-toggle','automation-master','headlights-toggle','idle-toggle']){
 const button=$(id);if(!button)continue;
 const glyph=button.querySelector('.spy-hardware-glyph');if(glyph)button.replaceChildren(document.createTextNode(glyph.textContent));
 button.removeAttribute('data-hardware-enabled');const tile=button.closest('.spy-tile');
 if(tile){tile.removeAttribute('data-power-state');tile.classList.remove('spy-on','spy-off')}
 const sync=()=>setGridVisual(button,button.classList.contains('active')&&!button.classList.contains('off')&&!button.disabled);
 new MutationObserver(sync).observe(button,{attributes:true,attributeFilter:['class','disabled']});sync();
}
const previousSyncChat=syncChat;
syncChat=function(){previousSyncChat();setGridVisual(chat.main,chatbot)};
setGridVisual(chat.main,chatbot);
syncIdle();syncVision();
})();
