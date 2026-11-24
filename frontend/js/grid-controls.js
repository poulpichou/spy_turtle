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
 button.classList.add('spy-tile-main');if(icon)button.textContent=icon;box.append(button);grid.append(box);return box;
}
function popup(title,items,anchor){
 document.querySelector('.spy-grid-popover')?.remove();
 const panel=document.createElement('div');panel.className='spy-grid-popover';panel.setAttribute('role','dialog');panel.setAttribute('aria-label',title);
 const heading=document.createElement('strong');heading.textContent=title;panel.append(heading);
 for(const item of items){const b=document.createElement('button');b.type='button';b.textContent=item.label;b.onclick=()=>{panel.remove();item.run()};panel.append(b)}
 document.body.append(panel);
 const rect=anchor.getBoundingClientRect(),pw=panel.getBoundingClientRect().width,ph=panel.getBoundingClientRect().height;
 panel.style.left=Math.max(5,Math.min(innerWidth-pw-5,rect.left))+'px';
 panel.style.top=(rect.bottom+ph+5<innerHeight?rect.bottom+4:Math.max(5,rect.top-ph-4))+'px';
 const close=e=>{if(!panel.contains(e.target)&&!anchor.contains(e.target)){panel.remove();document.removeEventListener('pointerdown',close,true)}};
 setTimeout(()=>document.addEventListener('pointerdown',close,true),0);
}
function choose(name,items){return event=>popup(name,items,event.currentTarget)}
function clickAdmin(action){const button=document.querySelector(`[data-admin-action="${action}"]`);if(button)button.click()}
const power=tile('Power','⏻',event=>popup('System actions',[
 {label:'Restart Turtle',run:()=>clickAdmin('restart')},{label:'Reboot Pi',run:()=>clickAdmin('reboot')},{label:'Shutdown Pi',run:()=>clickAdmin('shutdown')}
],event.currentTarget),{menu:event=>popup('System actions',[
 {label:'Restart Turtle',run:()=>clickAdmin('restart')},{label:'Reboot Pi',run:()=>clickAdmin('reboot')},{label:'Shutdown Pi',run:()=>clickAdmin('shutdown')}
],event.currentTarget)});
relocateButton('idle-toggle',leftGrid,'🌙');leftGrid.append(power.box);
const originalView=$('turtle-view-toggle');
if(originalView){originalView.classList.add('spy-legacy-hidden');originalView.parentElement?.classList.add('spy-legacy-row')}
let vision=localStorage.getItem('spy_grid_vision_mode')||'robot';
const visionTile=tile('Vision','🤖',()=>{}, {menu:event=>popup('Vision',[
 {label:'🤖 Robot — frames',run:()=>setVision('robot')},
 {label:'🐢 Turtle — emojis',run:()=>setVision('turtle')},
 {label:'🌡️ Thermal',run:()=>setVision('thermal')}
],event.currentTarget)});
function setVision(mode){
 vision=mode;localStorage.setItem('spy_grid_vision_mode',mode);
 if(mode!=='thermal'){
  const active=!!window.spyTurtleImageEffects?.isEnabled();
  if(active!==(mode==='turtle'))originalView?.click();
  document.querySelector('[data-view="camera"]')?.click();
 }else{
  if(window.spyTurtleImageEffects?.isEnabled())originalView?.click();
  document.querySelector('[data-view="thermal"]')?.click();
 }
 syncVision();
}
function syncVision(){const active=!!window.spyTurtleImageEffects?.isEnabled();if(vision!=='thermal')vision=active?'turtle':'robot';visionTile.main.textContent=vision==='turtle'?'🐢':vision==='thermal'?'🌡️':'🤖';visionTile.box.classList.toggle('selected',vision==='turtle')}
visionTile.main.onclick=event=>visionTile.box.querySelector('.spy-tile-arrow').click();
leftGrid.append(visionTile.box);
relocateButton('automation-master',leftGrid,'⚙️');
let chatbot=false;
const chat=tile('Chatbot','💬',()=>{chatbot=!chatbot;chat.box.classList.toggle('selected',chatbot);chat.main.setAttribute('aria-pressed',String(chatbot));chat.main.title='Chatbot UI placeholder (no listening or replies yet)'});
chat.main.setAttribute('aria-pressed','false');chat.main.title='Chatbot (UI placeholder only)';leftGrid.append(chat.box);
const langTile=tile('Language','🇫🇷',()=>{}, {menu:event=>popup('Language',[
 {label:'🇫🇷 Français',run:()=>setLanguage('fr')},{label:'🇬🇧 English',run:()=>setLanguage('en')}
],event.currentTarget)});
function setLanguage(lang){
 const target=document.querySelector(`#speech-language-options [data-value="${lang}"]`);
 target?.click();document.querySelector(`#message-language-buttons [data-lang="${lang}"]`)?.click();
 langTile.main.textContent=lang==='en'?'🇬🇧':'🇫🇷';localStorage.setItem('spy_grid_language',lang);
}
langTile.main.onclick=()=>langTile.box.querySelector('.spy-tile-arrow').click();
leftGrid.append(langTile.box);
const lang=document.querySelector('#speech-language-options .selected')?.dataset.value||localStorage.getItem('spy_grid_language')||'fr';
langTile.main.textContent=lang==='en'?'🇬🇧':'🇫🇷';
relocate('animation-toggle',rightGrid,'❤️');
const light=relocateButton('headlights-toggle',rightGrid,'💡');
if(light){
 const arrow=document.createElement('button');arrow.type='button';arrow.className='spy-tile-arrow';arrow.textContent='⌄';arrow.title='Headlight colors';arrow.onclick=event=>{
  const admin=$('headlight-presets'),picker=$('headlight-color-picker');
  const items=[...admin?.querySelectorAll('[data-color]')||[]].map(b=>({label:b.title||b.dataset.color,run:()=>b.click()}));
  if(picker)items.push({label:'🎨 Custom color…',run:()=>picker.click()});
  popup('Headlight colors',items,event.currentTarget);
 };light.append(arrow);
}
relocate('sound-toggle',rightGrid,'🔊');
relocate('eyes-toggle',rightGrid,'👀');
relocate('shell-light-toggle',rightGrid,'✨');
relocate('back-screen-toggle',rightGrid,'▭');
document.querySelector('.idle-lights-row')?.classList.add('spy-legacy-hidden');
function syncIdle(){document.body.classList.toggle('spy-grid-idle',idle.classList.contains('active')||idle.getAttribute('aria-pressed')==='true')}
document.addEventListener('turtlepowerchange',event=>{document.body.classList.toggle('spy-grid-idle',!!event.detail?.idle_mode);if(event.detail?.idle_mode){chatbot=false;chat.box.classList.remove('selected');chat.main.setAttribute('aria-pressed','false')}});
document.addEventListener('click',event=>{if(event.target===originalView||event.target?.dataset?.view)queueMicrotask(syncVision)});
const observer=new MutationObserver(()=>{syncIdle();syncVision()});
observer.observe(idle,{attributes:true,attributeFilter:['class','aria-pressed']});
if(originalView)observer.observe(originalView,{attributes:true,attributeFilter:['class','aria-pressed']});
syncIdle();syncVision();
})();
