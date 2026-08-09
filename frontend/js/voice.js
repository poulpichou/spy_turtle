const recordButton=document.getElementById("record-message");
const recordStatus=document.getElementById("record-status");
const listenButton=document.getElementById("listen-button");
const listenAudio=document.getElementById("listen-audio");
let recorder=null;
let recorderStream=null;
let recorderChunks=[];
let listening=false;

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
        recorderStream=null;
        recorder=null;
        recorderChunks=[];
        setTimeout(()=>{if(recordStatus.textContent==="Sent")recordStatus.textContent=""},1500);
    }
}

recordButton.onclick=async()=>{
    if(recorder&&recorder.state==="recording"){
        recorder.stop();
        recordButton.classList.remove("recording");
        recordButton.textContent="🎙️";
        return;
    }
    try{
        recorderStream=await navigator.mediaDevices.getUserMedia({audio:true});
        recorderChunks=[];
        recorder=new MediaRecorder(recorderStream);
        recorder.ondataavailable=event=>{if(event.data.size)recorderChunks.push(event.data)};
        recorder.onstop=sendRecordedMessage;
        recorder.start();
        recordButton.classList.add("recording");
        recordButton.textContent="■";
        recordStatus.textContent="Recording...";
    }catch(error){
        console.error("[VOICE RECORD]",error);
        recordStatus.textContent="Microphone denied";
        showCommandError(error);
    }
};

function stopListening(){
    listening=false;
    listenAudio.pause();
    listenAudio.removeAttribute("src");
    listenAudio.load();
    listenButton.classList.remove("active");
}

listenButton.onclick=async()=>{
    if(listening){stopListening();return}
    listening=true;
    listenButton.classList.add("active");
    listenAudio.src=`/audio/listen?t=${Date.now()}`;
    try{await listenAudio.play()}
    catch(error){
        console.error("[LISTEN]",error);
        stopListening();
        showCommandError(error);
    }
};
listenAudio.onerror=()=>{if(listening)stopListening()};
