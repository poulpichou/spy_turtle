(()=>{
 const mood=document.getElementById('emotion');if(!mood)return;
 async function refresh(){if(typeof transportMode!=='undefined'&&transportMode==='bluetooth')return;
  try{const r=await fetch('/state',{cache:'no-store'});if(!r.ok)return;const data=await r.json();mood.textContent=data.brain?.mood||data.brain?.emotion||'neutral';mood.title=data.brain?.mood_context_fr||''}catch{}
 }
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});setInterval(()=>{if(!document.hidden)refresh()},5000);refresh();
})();
