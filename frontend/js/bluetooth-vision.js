// Optional BLE Vision V2: one frame in flight, no backlog, no GATT reads.
const bleVision={active:false,token:0,serial:null,size:0,offset:0,bytes:null,resolve:null,reject:null,url:null,errors:0,source:null};
const bleVisionDelay=ms=>new Promise(r=>setTimeout(r,ms));
function bleVisionPacket(event){
    const v=event.target.value,b=new Uint8Array(v.buffer,v.byteOffset,v.byteLength);
    if(!bleVision.resolve||b.length<3)return;
    const serial=b[1]|b[2]<<8;
    if(b[0]===72){
        if(b.length<7)return;
        const size=new DataView(b.buffer,b.byteOffset,b.byteLength).getUint32(3,true);
        if(size<100||size>65535){bleVision.reject(new Error("Invalid BLE vision size"));return}
        bleVision.serial=serial;bleVision.size=size;bleVision.bytes=new Uint8Array(size);bleVision.offset=0;
    }else if(b[0]===68){
        if(b.length<5||bleVision.serial!==serial||!bleVision.bytes)return;
        const offset=b[3]|b[4]<<8,data=b.subarray(5);
        if(offset!==bleVision.offset||offset+data.length>bleVision.size){bleVision.reject(new Error("Missing BLE vision fragment"));return}
        bleVision.bytes.set(data,offset);bleVision.offset+=data.length;
        if(bleVision.offset===bleVision.size)bleVision.resolve(new Blob([bleVision.bytes],{type:"image/jpeg"}));
    }
}
async function bleVisionFrame(token,source,photoName=null){
    const characteristic=bluetoothCamera;
    if(!characteristic)throw new Error("Bluetooth vision characteristic unavailable");
    return new Promise((resolve,reject)=>{
        let done=false;
        const finish=(error,blob)=>{
            if(done)return;done=true;clearTimeout(timer);bleVision.resolve=null;bleVision.reject=null;
            error?reject(error):resolve(blob);
        };
        const timer=setTimeout(()=>finish(new Error("BLE vision timeout")),photoName?30000:5000);
        bleVision.serial=null;bleVision.bytes=null;
        bleVision.resolve=blob=>finish(null,blob);bleVision.reject=error=>finish(error);
        queueGatt(async()=>{
            if(token!==bleVision.token)throw new Error("BLE vision cancelled");
            const payload=photoName?new Uint8Array([80,...new TextEncoder().encode(photoName)]):new Uint8Array([source==="thermal"?84:78]);
            await characteristic.writeValueWithResponse(payload);
        }).catch(error=>finish(error));
    });
}
async function bleVisionLoop(token){
    const characteristic=bluetoothCamera;
    if(!characteristic)return;
    try{
        await queueGatt(()=>characteristic.startNotifications());
        characteristic.addEventListener("characteristicvaluechanged",bleVisionPacket);
        bleVision.active=true;
        while(token===bleVision.token&&transportMode==="bluetooth"&&bluetoothServer?.connected){
            const source=document.getElementById("thermal-view").classList.contains("active")?"thermal":document.getElementById("camera-view").classList.contains("active")?"camera":null;
            if(!source){await bleVisionDelay(250);continue}
            try{
                const start=performance.now(),blob=await bleVisionFrame(token,source);
                if(token!==bleVision.token)break;
                const url=URL.createObjectURL(blob),previous=bleVision.url;
                bleVision.url=url;bleVision.source=source;
                const target=document.getElementById(source==="thermal"?"thermal-stream":"camera-stream");target.src=url;
                if(previous)URL.revokeObjectURL(previous);
                bleVision.errors=0;
                console.debug(`[BLE VISION] ${blob.size} bytes, ${Math.round(performance.now()-start)} ms`);
            }catch(error){
                if(token!==bleVision.token)break;
                console.warn("[BLE VISION]",error);bleVision.errors++;
                if(bleVision.errors>=3){const target=document.getElementById(source==="thermal"?"thermal-stream":"camera-stream");target.removeAttribute("src");target.alt="Bluetooth vision unavailable"}
                await bleVisionDelay(700);
            }
            await bleVisionDelay(30);
        }
    }catch(error){console.warn("[BLE VISION] notifications unavailable",error);camera.alt="Bluetooth vision unavailable"}
    finally{
        bleVision.active=false;
        characteristic.removeEventListener("characteristicvaluechanged",bleVisionPacket);
        if(bleVision.reject)bleVision.reject(new Error("BLE vision stopped"));
        // Do not wait on stopNotifications during disconnect; it can reject on BlueZ.
        if(characteristic.service?.device?.gatt?.connected)queueGatt(()=>characteristic.stopNotifications()).catch(()=>{});
    }
}
async function blePhotoFetch(name){
    if(transportMode!=="bluetooth"||!bluetoothServer?.connected)throw new Error("Bluetooth disconnected");
    for(let i=0;i<20&&!bleVision.active;i++)await bleVisionDelay(100);
    if(!bleVision.active)throw new Error("Bluetooth notifications unavailable");
    return bleVisionFrame(bleVision.token,"photo",name);
}
document.addEventListener("transportchange",()=>{
    bleVision.token++;
    if(bleVision.reject)bleVision.reject(new Error("BLE vision transport changed"));
    if(bleVision.url){URL.revokeObjectURL(bleVision.url);bleVision.url=null;bleVision.source=null}
    if(transportMode==="bluetooth")bleVisionLoop(bleVision.token);
});
