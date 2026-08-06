const out=document.getElementById("admin-result");
function token(){const value=document.getElementById("admin-token").value.trim();sessionStorage.setItem("spy-admin-token",value);return value}
document.getElementById("admin-token").value=sessionStorage.getItem("spy-admin-token")||"";
async function post(path,body){
    const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json","X-Admin-Token":token()},body:body?JSON.stringify(body):null});
    const data=await response.json();
    if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);
    return data;
}
document.querySelectorAll("[data-admin-action]").forEach(button=>button.onclick=async()=>{
    const action=button.dataset.adminAction;
    if(!confirm(`Really ${action}?`))return;
    try{out.textContent=(await post(action==="restart"?"/admin/turtle/restart":`/admin/system/${action}`)).message}catch(error){out.textContent=error.message}
});
document.getElementById("wifi-add").onclick=async()=>{
    try{out.textContent=(await post("/admin/wifi",{ssid:document.getElementById("wifi-ssid").value.trim(),password:document.getElementById("wifi-password").value})).message}
    catch(error){out.textContent=error.message}
};
