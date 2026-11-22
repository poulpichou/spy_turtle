/* Spy Turtle Turtle's View V5: one-button mode, off by default, idle overrides it. */
(()=>{'use strict';
const button=document.getElementById('turtle-view-toggle'),idle=document.getElementById('idle-toggle');if(!button)return;
const api=window.spyTurtleImageEffects,key='spy_turtle_image_effects_v1';let isIdle=false;
// V5 deliberately starts with the eye OFF once, even when V4 was enabled.
const migration='spy_turtle_view_v5_initialized';if(!localStorage.getItem(migration)){api?.setEnabled(false);localStorage.setItem(migration,'1')}
function sync(){const active=!isIdle&&!!api?.isEnabled();button.classList.toggle('active',active);button.classList.toggle('off',!active);button.disabled=isIdle;button.setAttribute('aria-pressed',String(active));button.title=active?'Turtle’s View ON':'Turtle’s View OFF'}
button.onclick=()=>{if(isIdle||!api)return;api.setEnabled(!api.isEnabled());sync()};
document.addEventListener('turtlepowerchange',event=>{isIdle=!!event.detail?.idle_mode;if(isIdle)api?.setEnabled(false);sync()});
// Keep Admin checkbox and the eye in sync; manual effects never override the eye.
document.getElementById('image-effects-enabled')?.addEventListener('change',()=>{if(isIdle)api?.setEnabled(false);sync()});
document.getElementById('image-effects-manual')?.addEventListener('change',sync);
// Turtle's View should not activate while the robot is already idle on initial load.
if(idle?.classList.contains('active')){isIdle=true;api?.setEnabled(false)}sync();
})();
