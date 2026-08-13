const BLE_SERVICE_UUID="6f2d0001-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_COMMAND_UUID="6f2d0002-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_STATE_UUID="6f2d0003-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_ADMIN_UUID="6f2d0004-9b7e-4b2a-a1d3-53d9c4e8f210";
let transportMode="wifi";
let bluetoothDevice=null,bluetoothServer=null,bluetoothCommand=null,bluetoothState=null,bluetoothAdmin=null;
let bluetoothWriteQueue=Promise.resolve(),bluetoothAdminQueue=Promise.resolve();
let currentWifiName="--";

function transportLabel(){return transportMode==="bluetooth"?"Bluetooth":"Wi-Fi"}
function transportConnected(){return transportMode==="wifi"||!!bluetoothServer?.connected}
function updateTransportUI(){
    const button=document.getElementById("transport-toggle");
    if(button){button.textContent=transportMode==="bluetooth"?"ᛒ":"📶";button.classList.toggle("bluetooth",transportMode==="bluetooth")}
    const name=document.getElementById("transport-name");
    if(name)name.textContent=transportMode==="bluetooth"?`ᛒ ${bluetoothDevice?.name||"SpyTurtle"}`:`📶 ${currentWifiName}`;
}
function setWifiTransportName(name){currentWifiName=name||"Offline";updateTransportUI()}
function emitTransportChange(){document.dispatchEvent(new CustomEvent("transportchange",{detail:{mode:transportMode}}))}

async function connectBluetooth(){
    if(!navigator.bluetooth)throw new Error("Web Bluetooth is not supported by this browser");
    bluetoothDevice=await navigator.bluetooth.requestDevice({filters:[{services:[BLE_SERVICE_UUID]}]});
    bluetoothDevice.addEventListener("gattserverdisconnected",()=>{
        bluetoothServer=null;bluetoothCommand=null;bluetoothState=null;bluetoothAdmin=null;
        updateTransportUI();if(typeof setConnection==="function")setConnection("disconnected");emitTransportChange();
    });
    bluetoothServer=await bluetoothDevice.gatt.connect();
    const service=await bluetoothServer.getPrimaryService(BLE_SERVICE_UUID);
    bluetoothCommand=await service.getCharacteristic(BLE_COMMAND_UUID);
    bluetoothState=await service.getCharacteristic(BLE_STATE_UUID);
    bluetoothAdmin=await service.getCharacteristic(BLE_ADMIN_UUID);
    transportMode="bluetooth";
    updateTransportUI();emitTransportChange();
    if(typeof scheduleDashboard==="function")scheduleDashboard(0);
}
function useWifi(){
    transportMode="wifi";
    if(bluetoothDevice?.gatt?.connected)bluetoothDevice.gatt.disconnect();
    bluetoothServer=null;bluetoothCommand=null;bluetoothState=null;bluetoothAdmin=null;
    updateTransportUI();emitTransportChange();
    if(typeof scheduleDashboard==="function")scheduleDashboard(0);
}
async function writeBluetoothCommand(payload){
    if(!bluetoothCommand||!bluetoothServer?.connected)throw new Error("Bluetooth is not connected");
    const value=new TextEncoder().encode(JSON.stringify(payload));
    if(value.byteLength>400)throw new Error("Bluetooth command is too large");
    const write=async()=>{
        if(bluetoothCommand.writeValueWithResponse)return bluetoothCommand.writeValueWithResponse(value);
        return bluetoothCommand.writeValue(value);
    };
    bluetoothWriteQueue=bluetoothWriteQueue.then(write,write);
    return bluetoothWriteQueue;
}
async function readBluetoothState(){
    if(!bluetoothState||!bluetoothServer?.connected)throw new Error("Bluetooth is not connected");
    const value=await bluetoothState.readValue();
    return JSON.parse(new TextDecoder().decode(value));
}
async function bluetoothAdminRequest(action,data={}){
    if(!bluetoothAdmin||!bluetoothServer?.connected)throw new Error("Bluetooth is not connected");
    const task=async()=>{
        const payload=new TextEncoder().encode(JSON.stringify({action,data}));
        if(payload.byteLength>400)throw new Error("Bluetooth admin request is too large");
        if(bluetoothAdmin.writeValueWithResponse)await bluetoothAdmin.writeValueWithResponse(payload);
        else await bluetoothAdmin.writeValue(payload);
        const value=await bluetoothAdmin.readValue();
        const result=JSON.parse(new TextDecoder().decode(value));
        if(!result.ok)throw new Error(result.error||"Bluetooth admin command failed");
        return result;
    };
    bluetoothAdminQueue=bluetoothAdminQueue.then(task,task);
    return bluetoothAdminQueue;
}
document.addEventListener("DOMContentLoaded",()=>{
    updateTransportUI();
    const button=document.getElementById("transport-toggle");if(!button)return;
    button.onclick=async()=>{
        button.disabled=true;
        try{
            if(transportMode==="bluetooth")useWifi();
            else await connectBluetooth();
        }catch(error){console.error("[BLUETOOTH]",error);alert(`Bluetooth: ${error.message}`)}
        finally{button.disabled=false}
    };
});
