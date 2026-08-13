const BLE_SERVICE_UUID="6f2d0001-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_COMMAND_UUID="6f2d0002-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_STATE_UUID="6f2d0003-9b7e-4b2a-a1d3-53d9c4e8f210";
let transportMode="wifi";
let bluetoothDevice=null,bluetoothServer=null,bluetoothCommand=null,bluetoothState=null;
let bluetoothWriteQueue=Promise.resolve();

function transportLabel(){return transportMode==="bluetooth"?"BT":"Wi-Fi"}
function transportConnected(){return transportMode==="wifi"||!!bluetoothServer?.connected}
function updateTransportButton(){
    const button=document.getElementById("transport-toggle");if(!button)return;
    button.textContent=transportMode==="bluetooth"?"ᛒ BT":"📶 Wi-Fi";
    button.classList.toggle("bluetooth",transportMode==="bluetooth");
}
async function connectBluetooth(){
    if(!navigator.bluetooth)throw new Error("Web Bluetooth is not supported by this browser");
    bluetoothDevice=await navigator.bluetooth.requestDevice({filters:[{services:[BLE_SERVICE_UUID]}]});
    bluetoothDevice.addEventListener("gattserverdisconnected",()=>{bluetoothServer=null;bluetoothCommand=null;bluetoothState=null;updateTransportButton();if(typeof setConnection==="function")setConnection("disconnected")});
    bluetoothServer=await bluetoothDevice.gatt.connect();
    const service=await bluetoothServer.getPrimaryService(BLE_SERVICE_UUID);
    bluetoothCommand=await service.getCharacteristic(BLE_COMMAND_UUID);
    bluetoothState=await service.getCharacteristic(BLE_STATE_UUID);
    transportMode="bluetooth";
    updateTransportButton();
    if(typeof scheduleDashboard==="function")scheduleDashboard(0);
}
function useWifi(){
    transportMode="wifi";
    if(bluetoothDevice?.gatt?.connected)bluetoothDevice.gatt.disconnect();
    bluetoothServer=null;bluetoothCommand=null;bluetoothState=null;
    updateTransportButton();
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
document.addEventListener("DOMContentLoaded",()=>{
    updateTransportButton();
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
