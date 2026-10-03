const recordButton=document.getElementById("record-message");
const recordStatus=document.getElementById("record-status");
const listenButton=document.getElementById("listen-button");
let recorder=null;
let recorderStream=null;
let recorderChunks=[];
let listening=false;
let listenAbortController=null;
let listenAudioContext=null;
let listenGainNode=null;
let listenNextTime=0;
const LISTEN_GAIN=3.0;

function currentCenterView(){return document.querySelector(".center-tab.active")?.dataset.view||"camera"}

document.getElementById("photo-button").onclick=async()=>{
    try{
        const source=currentCenterView()==="thermal"?"thermal":"camera";
        const response=await fetch(`/photos/capture?source=${source}`,{method:"POST"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        if(currentCenterView()==="photos"&&typeof loadPhotos==="function")await loadPhotos();
    }catch(error){showCommandError(error)}
};

function encodeWav(buffer){
    const channels=buffer.numberOfChannels;
    const length=buffer.length;
    const sampleRate=buffer.sampleRate;
    const data=new Int16Array(length);
    for(let i=0;i<length;i++){
        let sample=0;
        for(let channel=0;channel<channels;channel++)sample+=buffer.getChannelData(channel)[i];
        sample=Math.max(-1,Math.min(1,sample/channels));
        data[i]=sample<0?sample*32768:sample*32767;
    }
    const output=new ArrayBuffer(44+data.byteLength);
    const view=new DataView(output);
    const write=(offset,text)=>{for(let i=0;i<text.length;i++)view.setUint8(offset+i,text.charCodeAt(i))};
    write(0,"RIFF");view.setUint32(4,36+data.byteLength,true);write(8,"WAVE");write(12,"fmt ");
    view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);view.setUint32(24,sampleRate,true);
    view.setUint32(28,sampleRate*2,true);view.setUint16(32,2,true);view.setUint16(34,16,true);write(36,"data");view.setUint32(40,data.byteLength,true);
    new Int16Array(output,44).set(data);
    return output;
}

async function sendRecordedMessage(){
    recordStatus.textContent="Sending...";
    try{
        const blob=new Blob(recorderChunks,{type:recorder.mimeType});
        const context=new (window.AudioContext||window.webkitAudioContext)();
        const decoded=await context.decodeAudioData(await blob.arrayBuffer());
        const wav=encodeWav(decoded);
        await context.close();
        const response=await fetch("/audio/message",{method:"POST",headers:{"Content-Type":"audio/wav"},body:wav});
        if(!response.ok)throw new Error((await response.text())||`HTTP ${response.status}`);
        recordStatus.textContent="Sent";
    }catch(error){
        console.error("[VOICE MESSAGE]",error);
        recordStatus.textContent="Failed";
        showCommandError(error);
    }finally{
        recorderStream?.getTracks().forEach(track=>track.stop());
        recorderStream=null;recorder=null;recorderChunks=[];
        setTimeout(()=>{if(recordStatus.textContent==="Sent")recordStatus.textContent=""},1500);
    }
}

recordButton.onclick=async()=>{
    if(recorder&&recorder.state==="recording"){
        recorder.stop();recordButton.classList.remove("recording");recordButton.textContent="ðŸŽ™ï¸";return;
    }
    try{
        recorderStream=await navigator.mediaDevices.getUserMedia({audio:true});
        recorderChunks=[];recorder=new MediaRecorder(recorderStream);
        recorder.ondataavailable=event=>{if(event.data.size)recorderChunks.push(event.data)};
        recorder.onstop=sendRecordedMessage;recorder.start();
        recordButton.classList.add("recording");recordButton.textContent="â– ";recordStatus.textContent="Recording...";
    }catch(error){
        console.error("[VOICE RECORD]",error);recordStatus.textContent="Microphone denied";showCommandError(error);
    }
};

function playPcmChunk(bytes){
    if(!listenAudioContext||bytes.byteLength<2)return;
    const sampleCount=Math.floor(bytes.byteLength/2);
    const samples=new Float32Array(sampleCount);
    const view=new DataView(bytes.buffer,bytes.byteOffset,sampleCount*2);
    for(let i=0;i<sampleCount;i++)samples[i]=view.getInt16(i*2,true)/32768;
    const buffer=listenAudioContext.createBuffer(1,sampleCount,16000);
    buffer.copyToChannel(samples,0);
    const source=listenAudioContext.createBufferSource();
    source.buffer=buffer;source.connect(listenGainNode);
    const now=listenAudioContext.currentTime;
    if(listenNextTime<now+0.05)listenNextTime=now+0.05;
    source.start(listenNextTime);
    listenNextTime+=buffer.duration;
}

async function startListening(){
    if(listening)return;
    listening=true;listenButton.classList.add("active");
    listenAbortController=new AbortController();
    listenAudioContext=new (window.AudioContext||window.webkitAudioContext)({sampleRate:16000});
    listenGainNode=listenAudioContext.createGain();
    listenGainNode.gain.value=LISTEN_GAIN;
    listenGainNode.connect(listenAudioContext.destination);
    await listenAudioContext.resume();
    listenNextTime=listenAudioContext.currentTime+0.08;
    let carry=null;
    try{
        const response=await fetch(`/audio/listen?t=${Date.now()}`,{signal:listenAbortController.signal,cache:"no-store"});
        if(!response.ok)throw new Error((await response.text())||`HTTP ${response.status}`);
        if(!response.body)throw new Error("Streaming response unavailable");
        const reader=response.body.getReader();
        while(listening){
            const {value,done}=await reader.read();
            if(done)break;
            let chunk=value;
            if(carry!==null){
                const merged=new Uint8Array(chunk.length+1);merged[0]=carry;merged.set(chunk,1);chunk=merged;carry=null;
            }
            if(chunk.length%2){carry=chunk[chunk.length-1];chunk=chunk.slice(0,-1)}
            if(chunk.length)playPcmChunk(chunk);
        }
    }catch(error){
        if(error.name!=="AbortError"&&listening){
            console.error("[LISTEN]",error);showCommandError(error);
        }
    }finally{
        if(listening)await stopListening();
    }
}

async function stopListening(){
    if(!listening&&!listenAudioContext)return;
    listening=false;listenButton.classList.remove("active");
    listenAbortController?.abort();listenAbortController=null;
    const context=listenAudioContext;listenAudioContext=null;listenGainNode=null;listenNextTime=0;
    if(context&&context.state!=="closed"){
        try{await context.close()}catch(error){console.debug("[LISTEN] close",error)}
    }
}

listenButton.onclick=()=>{if(listening)stopListening();else startListening()};
