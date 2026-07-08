async function updateDashboard(){
    const status=await getStatus();

    document.getElementById("battery").innerText=status.battery;
    document.getElementById("wifi").innerText=status.wifi?"OK":"OFF";
    document.getElementById("emotion").innerText=status.emotion;
    document.getElementById("led-mode").innerText=status.led_mode;
    document.getElementById("motion").innerText=status.motion;
}

setInterval(updateDashboard,1000);
updateDashboard();