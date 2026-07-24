const compactDropdowns=[];
function closeCompactDropdowns(except=null){compactDropdowns.forEach(item=>{if(item!==except)item.wrapper.classList.remove("open")})}
function createCompactDropdown(select){
    const wrapper=document.createElement("div"),button=document.createElement("button"),menu=document.createElement("div");
    wrapper.className="compact-select";button.type="button";button.className="compact-select-button";menu.className="compact-select-menu";
    select.parentNode.insertBefore(wrapper,select);wrapper.append(select,button,menu);select.classList.add("compact-select-native");
    const item={wrapper,button,menu,select};compactDropdowns.push(item);
    function rebuild(){
        menu.replaceChildren();
        [...select.options].forEach(option=>{
            const choice=document.createElement("button");
            choice.type="button";choice.className="compact-select-option";choice.textContent=option.textContent;choice.dataset.value=option.value;
            choice.onclick=()=>{select.value=option.value;select.dispatchEvent(new Event("change",{bubbles:true}));update();wrapper.classList.remove("open")};
            menu.appendChild(choice);
        });
    }
    function update(){
        button.textContent=select.selectedOptions[0]?.textContent||"Select";
        [...menu.children].forEach(choice=>choice.classList.toggle("selected",choice.dataset.value===select.value));
    }
    button.onclick=event=>{event.stopPropagation();const opening=!wrapper.classList.contains("open");closeCompactDropdowns(item);wrapper.classList.toggle("open",opening)};
    select.addEventListener("change",update);rebuild();update();
    new MutationObserver(()=>{rebuild();update()}).observe(select,{childList:true,subtree:true});
}
document.querySelectorAll("select").forEach(createCompactDropdown);
document.addEventListener("click",()=>closeCompactDropdowns());
document.addEventListener("keydown",event=>{if(event.key==="Escape")closeCompactDropdowns()});
