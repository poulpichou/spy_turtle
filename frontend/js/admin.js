const adminResult=document.getElementById("admin-result");

async function adminPost(path,body){
    const response=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):null});
    const data=await response.json();
    if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);
    return data;
}

document.querySelectorAll("[data-admin-action]").forEach(button=>button.onclick=async()=>{
    const action=button.dataset.adminAction;
    const labels={restart:"restart Spy Turtle",reboot:"reboot the Raspberry Pi",shutdown:"shut down the Raspberry Pi"};
    if(!confirm(`Really ${labels[action]}?`))return;
    try{
        const path=action==="restart"?"/admin/turtle/restart":`/admin/system/${action}`;
        adminResult.textContent=(await adminPost(path)).message;
    }catch(error){adminResult.textContent=error.message}
});

document.getElementById("wifi-add").onclick=async()=>{
    const ssid=document.getElementById("wifi-ssid").value.trim();
    const password=document.getElementById("wifi-password").value;
    if(!ssid||!password){adminResult.textContent="SSID and password are required";return}
    try{
        adminResult.textContent=(await adminPost("/admin/wifi",{ssid,password})).message;
        document.getElementById("wifi-password").value="";
    }catch(error){adminResult.textContent=error.message}
};
