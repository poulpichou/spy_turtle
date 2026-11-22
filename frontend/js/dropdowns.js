const compactDropdowns=[];
const spyPickerIds={"animation-select":["Mood","moods"],"sound-select":["Sounds","audio"],"face-select":["Eyes","faces"],"shell-select":["Back screens","shell"],"led-select":["LEDs","leds"]};
const spyPickerIcons={status:'📊',log:'📜',rocket:'🚀',dance:'💃',smoke:'💨',fire:'🔥',sleep:'😴',leds:'💡',countdown:'⏳',loading:'⌛',glasses:'😎',glasses_large:'😎',happy:'😊',rocket_turtle:'🚀',walking:'🚶',off:'⚫',headlights:'🔦',neutral:'😐',rainbow:'🌈',breathing:'🫧',pulse:'💓',spinner:'🌀',wave:'🌊',police:'🚨',fart:'💨',cool:'😎',blink:'😉',surprised:'😮',angry:'😠',curious:'🤔',sad:'😢',yawn:'🥱',love:'🥰',excited:'🤩',scared:'😨',gassy:'💨',dreamy:'💭'};
const spyMoodStyles=[['gassy','💨','gassy'],['dreamy','💭','dreamy'],['neutral','😐','neutral'],['happy','😊','happy'],['angry','😠','angry'],['sleep','😴','sleepy'],['curious','🤔','curious'],['surpris','😮','curious'],['sad','😢','sleepy'],['love','🥰','happy'],['scared','😨','sleepy'],['excited','🤩','happy']];
let spyPicker=null,spyPickerActive=null;
function spyPickerLabel(section,option){
    const name=option.value.toLowerCase(),label=option.textContent.trim();
    if(section==='moods'){const mood=spyMoodStyles.find(([key])=>name.includes(key));return {label:mood?`${mood[1]} ${label}`:label,tone:mood?.[2]||''}}
    if(section==='audio')return {label,tone:''};
    const icon=spyPickerIcons[name]||spyPickerIcons[name.split('_')[0]];
    return {label:icon?`${icon} ${label}`:label,tone:''};
}
function closeSpyPicker(){if(!spyPicker)return;spyPicker.hidden=true;spyPickerActive=null;document.body.classList.remove('spy-picker-open')}
function ensureSpyPicker(){
    if(spyPicker)return spyPicker;
    const overlay=document.createElement('div');overlay.className='spy-picker-overlay';overlay.hidden=true;overlay.innerHTML='<div class="spy-picker-panel" role="dialog" aria-modal="true" aria-label="Choose option"><div class="spy-picker-head"><strong class="spy-picker-title"></strong><button type="button" class="spy-picker-close" aria-label="Close">×</button></div><div class="spy-picker-grid"></div></div>';
    overlay.addEventListener('click',event=>{if(event.target===overlay)closeSpyPicker()});overlay.querySelector('.spy-picker-close').onclick=closeSpyPicker;document.body.append(overlay);spyPicker=overlay;return overlay;
}
function openSpyPicker(item){
    const overlay=ensureSpyPicker(),grid=overlay.querySelector('.spy-picker-grid');spyPickerActive=item;
    overlay.querySelector('.spy-picker-title').textContent=item.title;grid.replaceChildren();
    for(const option of item.select.options){
        if(option.disabled||!option.value)continue;
        const style=spyPickerLabel(item.section,option),choice=document.createElement('button');choice.type='button';choice.className='spy-picker-choice';choice.textContent=style.label;choice.title=option.textContent;
        if(style.tone)choice.dataset.moodTone=style.tone;
        if(option.value===item.select.value)choice.classList.add('selected');
        choice.onclick=()=>{item.select.value=option.value;item.select.dispatchEvent(new Event('change',{bubbles:true}));closeSpyPicker()};grid.append(choice);
    }
    if(!grid.children.length){const empty=document.createElement('span');empty.textContent='No options available';grid.append(empty)}
    overlay.hidden=false;document.body.classList.add('spy-picker-open');grid.scrollTop=0;
}
function closeCompactDropdowns(except=null){compactDropdowns.forEach(item=>{if(item!==except)item.wrapper.classList.remove('open')})}
function createCompactDropdown(select){
    const wrapper=document.createElement('div'),button=document.createElement('button'),menu=document.createElement('div');
    wrapper.className='compact-select';button.type='button';button.className='compact-select-button';menu.className='compact-select-menu';
    select.parentNode.insertBefore(wrapper,select);wrapper.append(select,button,menu);select.classList.add('compact-select-native');
    const config=spyPickerIds[select.id],item={wrapper,button,menu,select,title:config?.[0],section:config?.[1]};compactDropdowns.push(item);
    function rebuild(){
        if(config)return;
        menu.replaceChildren();
        [...select.options].forEach(option=>{
            const choice=document.createElement('button');choice.type='button';choice.className='compact-select-option';choice.textContent=option.textContent;choice.dataset.value=option.value;
            choice.onclick=()=>{select.value=option.value;select.dispatchEvent(new Event('change',{bubbles:true}));update();wrapper.classList.remove('open')};menu.append(choice);
        });
    }
    function update(){button.textContent=select.selectedOptions[0]?.textContent||'Select';[...menu.children].forEach(choice=>choice.classList.toggle('selected',choice.dataset.value===select.value))}
    button.onclick=event=>{event.stopPropagation();if(config){closeCompactDropdowns();openSpyPicker(item);return}const opening=!wrapper.classList.contains('open');closeCompactDropdowns(item);wrapper.classList.toggle('open',opening)};
    select.addEventListener('change',update);rebuild();update();new MutationObserver(()=>{rebuild();update()}).observe(select,{childList:true,subtree:true});
}
document.querySelectorAll('select').forEach(createCompactDropdown);
document.addEventListener('click',()=>closeCompactDropdowns());
document.addEventListener('keydown',event=>{if(event.key==='Escape'){closeCompactDropdowns();closeSpyPicker()}});
document.addEventListener('transportchange',closeSpyPicker);
