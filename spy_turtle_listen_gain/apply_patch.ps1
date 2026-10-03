$ErrorActionPreference="Stop"
if(!(Test-Path ".\frontend\js\voice.js")){throw "Run from spy_turtle root."}
$p=".\frontend\js\voice.js"
$c=Get-Content $p -Raw

if($c -notmatch 'const LISTEN_GAIN'){
$c=$c -replace 'let listenNextTime=0;',"let listenNextTime=0;`r`nconst LISTEN_GAIN=3.0;"
}
if($c -notmatch 'let listenGainNode'){
$c=$c -replace 'let listenAudioContext=null;',"let listenAudioContext=null;`r`nlet listenGainNode=null;"
}
$c=$c -replace [regex]::Escape('listenAudioContext=new (window.AudioContext||window.webkitAudioContext)({sampleRate:16000});
    await listenAudioContext.resume();'),
'listenAudioContext=new (window.AudioContext||window.webkitAudioContext)({sampleRate:16000});
    listenGainNode=listenAudioContext.createGain();
    listenGainNode.gain.value=LISTEN_GAIN;
    listenGainNode.connect(listenAudioContext.destination);
    await listenAudioContext.resume();'

$c=$c -replace 'source\.buffer=buffer;source\.connect\(listenAudioContext\.destination\);','source.buffer=buffer;source.connect(listenGainNode);'
$c=$c -replace 'const context=listenAudioContext;listenAudioContext=null;listenNextTime=0;','const context=listenAudioContext;listenAudioContext=null;listenGainNode=null;listenNextTime=0;'

Set-Content $p $c -Encoding utf8 -NoNewline
Write-Host "Listen gain = 3.0x"
