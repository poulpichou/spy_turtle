(() => {
    const modal=document.getElementById("message-modal"),editor=modal?.querySelector(".message-editor");
    if(!modal||!editor)return;
    function resize(){
        const viewport=window.visualViewport;
        const height=viewport?.height||window.innerHeight;
        editor.style.setProperty("--spy-visible-height",`${Math.floor(height)}px`);
        modal.style.top=`${Math.max(0,Math.floor(viewport?.offsetTop||0))}px`;
        modal.style.height=`${Math.floor(height)}px`;
        modal.style.bottom="auto";
    }
    window.visualViewport?.addEventListener("resize",resize);
    window.visualViewport?.addEventListener("scroll",resize);
    window.addEventListener("resize",resize);
    document.getElementById("screen-message-button")?.addEventListener("click",resize);
    resize();
})();
