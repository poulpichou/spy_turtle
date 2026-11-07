const BLE_SERVICE_UUID="6f2d0001-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_COMMAND_UUID="6f2d0002-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_STATE_UUID="6f2d0003-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_ADMIN_UUID="6f2d0004-9b7e-4b2a-a1d3-53d9c4e8f210";
const BLE_CAMERA_UUID="6f2d0005-9b7e-4b2a-a1d3-53d9c4e8f210";
let transportMode="wifi";
let bluetoothDevice=null,bluetoothServer=null,bluetoothCommand=null,bluetoothState=null,bluetoothAdmin=null,bluetoothCamera=null;
let bluetoothQueue=Promise.resolve(),bluetoothPending=0,bluetoothEpoch=0;
let bluetoothCachedState=null,bluetoothCachedAt=0;
let bluetoothMoveEpoch=0;
function queueGatt(task,{lowPriority=false,moveEpoch=null}={}){
    if(lowPriority&&bluetoothPending)return Promise.resolve(bluetoothCachedState);
    const epoch=bluetoothEpoch;
    bluetoothPending++;
    const run=async()=>{
        if(epoch!==bluetoothEpoch||!bluetoothServer?.connected)throw new Error("Bluetooth disconnected");
        if(moveEpoch!==null&&moveEpoch!==bluetoothMoveEpoch)return;
        return task();
    };
    const result=bluetoothQueue.then(run,run);
    bluetoothQueue=result.catch(()=>{});
    return result.finally(()=>{bluetoothPending=Math.max(0,bluetoothPending-1)});
}
function invalidateBluetooth(){bluetoothEpoch++;bluetoothMoveEpoch++;bluetoothCachedState=null;bluetoothCachedAt=0}

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
        invalidateBluetooth();bluetoothServer=null;bluetoothCommand=null;bluetoothState=null;bluetoothAdmin=null;bluetoothCamera=null;
        updateTransportUI();if(typeof setConnection==="function")setConnection("disconnected");emitTransportChange();
    });
    bluetoothServer=await bluetoothDevice.gatt.connect();
    const service=await bluetoothServer.getPrimaryService(BLE_SERVICE_UUID);
    bluetoothCommand=await service.getCharacteristic(BLE_COMMAND_UUID);
    bluetoothState=await service.getCharacteristic(BLE_STATE_UUID);
    bluetoothAdmin=await service.getCharacteristic(BLE_ADMIN_UUID);
    try{bluetoothCamera=await service.getCharacteristic(BLE_CAMERA_UUID)}catch(error){bluetoothCamera=null;console.warn("[BLE VISION] optional camera unavailable",error)}
    transportMode="bluetooth";
    updateTransportUI();emitTransportChange();
    if(typeof scheduleDashboard==="function")scheduleDashboard(0);
}
function useWifi(){
    transportMode="wifi";
    if(bluetoothDevice?.gatt?.connected)bluetoothDevice.gatt.disconnect();
    invalidateBluetooth();bluetoothServer=null;bluetoothCommand=null;bluetoothState=null;bluetoothAdmin=null;bluetoothCamera=null;
    updateTransportUI();emitTransportChange();
    if(typeof scheduleDashboard==="function")scheduleDashboard(0);
}
async function writeBluetoothCommand(payload){
    if(!bluetoothCommand||!bluetoothServer?.connected)throw new Error("Bluetooth is not connected");
    const value=new TextEncoder().encode(JSON.stringify(payload));
    if(value.byteLength>400)throw new Error("Bluetooth command is too large");
    const isMove=payload.type==="move";
    if(isMove&&payload.value==="stop")bluetoothMoveEpoch++;
    const moveEpoch=isMove&&payload.value!=="stop"?bluetoothMoveEpoch:null;
    return queueGatt(async()=>{
        if(bluetoothCommand.writeValueWithResponse)return bluetoothCommand.writeValueWithResponse(value);
        return bluetoothCommand.writeValue(value);
    },{moveEpoch});
}
async function readBluetoothState(){
    if(!bluetoothState||!bluetoothServer?.connected)throw new Error("Bluetooth is not connected");
    if(bluetoothPending&&bluetoothCachedState)return bluetoothCachedState;
    const result=await queueGatt(async()=>{
        const value=await bluetoothState.readValue();
        const data=JSON.parse(new TextDecoder().decode(value));
        bluetoothCachedState=data;bluetoothCachedAt=Date.now();return data;
    },{lowPriority:!!bluetoothCachedState});
    return result||bluetoothCachedState||{};
}
async function bluetoothAdminRequest(action,data={}){
    if(!bluetoothAdmin||!bluetoothServer?.connected)throw new Error("Bluetooth is not connected");
    return queueGatt(async()=>{
        const payload=new TextEncoder().encode(JSON.stringify({action,data}));
        if(payload.byteLength>400)throw new Error("Bluetooth admin request is too large");
        if(bluetoothAdmin.writeValueWithResponse)await bluetoothAdmin.writeValueWithResponse(payload);
        else await bluetoothAdmin.writeValue(payload);
        const value=await bluetoothAdmin.readValue();
        const result=JSON.parse(new TextDecoder().decode(value));
        if(!result.ok)throw new Error(result.error||"Bluetooth admin command failed");
        return result;
    });
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

async function turtleRequest(path,body=null){
    if(transportMode==="bluetooth"){
        const actions={"/brain/moods":"mood_status","/brain/moods/list":"mood_list","/brain/moods/select":"mood_select","/brain/headlights":"headlights","/brain/head-movements":"head_movements","/sentinel/status":"sentinel_status","/sentinel/enable":"sentinel_enable","/automation/status":"automation_status","/automation/enable":"automation_enable","/automation/sounds":"automation_sounds"};
        const action=actions[path];if(!action)throw Error(`Unsupported Bluetooth feature: ${path}`);
        return bluetoothAdminRequest(action,body||{});
    }
    const response=await fetch(path,{method:body===null?"GET":"POST",headers:{"Content-Type":"application/json"},body:body===null?undefined:JSON.stringify(body),cache:"no-store"});
    const data=await response.json();if(!response.ok)throw Error(data.detail||`HTTP ${response.status}`);return data;
}
