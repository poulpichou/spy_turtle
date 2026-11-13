// Spy Turtle remote entry: never switch to a remote robot without user confirmation.
// Navigation (rather than cross-origin API calls) preserves existing camera, audio and BLE code.
(()=>{
    const LOCAL='https://spyturtle.local/';
    const REMOTE='https://spyturtle.taile25b0a.ts.net/';
    const remote=location.hostname==='spyturtle.taile25b0a.ts.net';
    const target=remote?LOCAL:REMOTE;
    const label=remote?'LOCAL':'REMOTE';
    function banner(){
        const bar=document.createElement('div');bar.id='remote-access-bar';
        bar.style.cssText='position:fixed;bottom:8px;right:8px;z-index:9998;background:#17212c;color:#fff;border:1px solid #718096;border-radius:9px;padding:5px 8px;display:flex;gap:7px;align-items:center;font:12px sans-serif;box-shadow:0 2px 12px #0008';
        const mode=document.createElement('strong');mode.textContent=remote?'🌐 REMOTE':'📶 LOCAL';
        const button=document.createElement('button');button.type='button';button.textContent=remote?'Try local Wi-Fi':'Remote access';button.style.cssText='font:12px sans-serif;padding:5px 8px;border-radius:6px';
        button.onclick=()=>{
            if(!remote&&!confirm('Connect to Spy Turtle remotely over Tailscale?\n\nOnly continue if you intend to control the robot from a distance.'))return;
            location.assign(target);
        };
        bar.append(mode,button);document.body.append(bar);
    }
    document.addEventListener('DOMContentLoaded',banner);
})();
