async function updateDashboard(){
    const status=await getStatus();

    document.getElementById("battery").innerText=status.battery;
    document.getElementById("wifi").innerText="OK";
    document.getElementById("emotion").innerText=status.emotion;
    document.getElementById("led-mode").innerText=status.led_mode;
    document.getElementById("motion").innerText=status.motion||"stop";
}

setInterval(updateDashboard,1000);
updateDashboard();