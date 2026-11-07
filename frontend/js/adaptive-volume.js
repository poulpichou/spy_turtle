(() => {
 const toggle=document.getElementById("adaptive-volume"),status=document.getElementById("adaptive-volume-status");
 if(!toggle||!status)return;
 async function call(method,body){
  const response=await fetch("/admin/audio/adaptive",{method,headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined,cache:"no-store"});
  const data=await response.json();if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);return data;
 }
 function render(data){toggle.checked=!!data.enabled;status.textContent=`${data.enabled?"On":"Off"} · boost ${data.boost||0}% · ambient RMS ${data.ambient_rms??"--"}${data.error?" · "+data.error:""}`}
 async function refresh(){try{render(await call("GET"))}catch(e){status.textContent=e.message}}
 toggle.onchange=async()=>{toggle.disabled=true;try{render(await call("POST",{enabled:toggle.checked}))}catch(e){status.textContent=e.message;await refresh()}finally{toggle.disabled=false}};
 document.addEventListener("transportchange",refresh);refresh();
 setInterval(()=>{if(document.getElementById("admin-view")?.classList.contains("active"))refresh()},10000);
})();
