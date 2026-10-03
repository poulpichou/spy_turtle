$ErrorActionPreference = "Stop"
$Patch = Join-Path $PWD "spy_turtle_live_listen_fix"

if (-not (Test-Path ".\robot\api\app.py") -or -not (Test-Path ".\frontend\js\voice.js")) {
    throw "Run this script from the root of the spy_turtle repository."
}
if (-not (Test-Path "$Patch\frontend\js\voice.js")) {
    throw "Patch folder not found at: $Patch"
}

Write-Host "Applying live microphone listen fix..." -ForegroundColor Cyan
Copy-Item "$Patch\frontend\js\voice.js" ".\frontend\js\voice.js" -Force

$Path=".\robot\api\app.py"
$Content=Get-Content $Path -Raw

$Old=@'
def microphone_chunks():
    command=["arecord","-q","-D",settings.MICROPHONE_DEVICE,"-f","S16_LE","-r",str(settings.MICROPHONE_RATE),"-c",str(settings.MICROPHONE_CHANNELS),"-t","wav"]
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    log.info(f"[MICROPHONE] listen start device={settings.MICROPHONE_DEVICE}")
    try:
        while process.stdout:
            chunk=process.stdout.read(4096)
            if not chunk:break
            yield chunk
    finally:
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=1)
        except subprocess.TimeoutExpired:process.kill()
        log.info("[MICROPHONE] listen stop")
'@

$New=@'
def microphone_chunks():
    command=["arecord","-q","-D",settings.MICROPHONE_DEVICE,"-f","S16_LE","-r",str(settings.MICROPHONE_RATE),"-c",str(settings.MICROPHONE_CHANNELS),"-t","raw"]
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    log.info(f"[MICROPHONE] listen start device={settings.MICROPHONE_DEVICE} format=raw-pcm")
    try:
        while process.stdout:
            chunk=process.stdout.read(4096)
            if not chunk:break
            yield chunk
    finally:
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=1)
        except subprocess.TimeoutExpired:process.kill()
        log.info("[MICROPHONE] listen stop")
'@

if ($Content.Contains($Old)) {$Content=$Content.Replace($Old,$New)}
elseif ($Content -notmatch 'format=raw-pcm') {throw "Could not patch microphone_chunks() in robot/api/app.py"}

$Old='return StreamingResponse(microphone_chunks(),media_type="audio/wav",headers={"Cache-Control":"no-store"})'
$New='return StreamingResponse(microphone_chunks(),media_type="application/octet-stream",headers={"Cache-Control":"no-store","X-Audio-Format":"s16le","X-Audio-Rate":str(settings.MICROPHONE_RATE),"X-Audio-Channels":str(settings.MICROPHONE_CHANNELS)})'
if ($Content.Contains($Old)) {$Content=$Content.Replace($Old,$New)}
elseif ($Content -notmatch 'X-Audio-Format') {throw "Could not patch /audio/listen StreamingResponse"}

Set-Content $Path $Content -Encoding utf8 -NoNewline

if (Test-Path ".\.venv\Scripts\python.exe") {$Python=".\.venv\Scripts\python.exe"}
elseif (Get-Command python -ErrorAction SilentlyContinue) {$Python="python"}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {$Python="python3"}
else {throw "No Python interpreter found."}

& $Python -m py_compile ".\robot\api\app.py"
if ($LASTEXITCODE -ne 0) {throw "app.py syntax validation failed."}

Write-Host ""
Write-Host "Live listen fix applied." -ForegroundColor Green
Write-Host "- backend now streams raw PCM instead of an endless WAV"
Write-Host "- frontend plays PCM with AudioContext"
Write-Host "- Listen toggle now stops with AbortController (no pause()/play() race)"
Write-Host ""
git status --short
git diff --stat
