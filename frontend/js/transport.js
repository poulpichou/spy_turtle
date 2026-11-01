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
    bluetoothCamera=await service.getCharacteristic(BLE_CAMERA_UUID);
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
async function readBluetoothCameraFrame(){
    if(!bluetoothCamera||!bluetoothServer?.connected)throw new Error("Bluetooth camera unavailable");
    const camera=bluetoothCamera,epoch=bluetoothEpoch;
    const write=async(value)=>{if(camera.writeValueWithResponse)return camera.writeValueWithResponse(value);return camera.writeValue(value)};
    const header=await queueGatt(async()=>{
        await write(new Uint8Array([78]));
        return bluetoothCamera.readValue();
    });
    const meta=new DataView(header.buffer,header.byteOffset,header.byteLength);
    if(meta.byteLength<6)throw new Error("Invalid BLE camera header");
    const size=meta.getUint32(0,true);
    if(size<100||size>65535)throw new Error(`Invalid BLE JPEG size: ${size}`);
    const image=new Uint8Array(size);
    for(let offset=0;offset<size;){
        if(epoch!==bluetoothEpoch||transportMode!=="bluetooth")throw new Error("Camera transfer cancelled");
        const chunk=await queueGatt(async()=>{
            const request=new Uint8Array(5);request[0]=67;new DataView(request.buffer).setUint32(1,offset,true);
            await write(request);return bluetoothCamera.readValue();
        });
        const bytes=new Uint8Array(chunk.buffer,chunk.byteOffset,chunk.byteLength);
        if(!bytes.length||bytes.length>size-offset)throw new Error("Invalid BLE camera chunk");
        image.set(bytes,offset);offset+=bytes.length;
    }
    return new Blob([image],{type:"image/jpeg"});
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
