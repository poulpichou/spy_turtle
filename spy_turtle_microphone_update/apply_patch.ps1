$ErrorActionPreference = "Stop"
$Patch = Join-Path $PWD "spy_turtle_microphone_update"

if (-not (Test-Path ".\robot\config\settings.py") -or
    -not (Test-Path ".\robot\api\app.py") -or
    -not (Test-Path ".\robot\shell\ui\touch_views.py") -or
    -not (Test-Path ".\docs\wiring.md")) {
    throw "Run this script from the root of the spy_turtle repository."
}
if (-not (Test-Path "$Patch\scripts\test_microphone.sh")) {
    throw "Patch folder not found at: $Patch"
}

Write-Host "Applying USB microphone integration..." -ForegroundColor Cyan
Copy-Item "$Patch\scripts\test_microphone.sh" ".\scripts\test_microphone.sh" -Force

# settings.py
$Path=".\robot\config\settings.py"
$Content=Get-Content $Path -Raw
if ($Content -notmatch 'MICROPHONE_ENABLED=') {
    $Content=$Content.Replace("# USB microphone`r`n","# USB microphone`r`nMICROPHONE_ENABLED=True`r`n")
    $Content=$Content.Replace("# USB microphone`n","# USB microphone`nMICROPHONE_ENABLED=True`n")
} else {
    $Content=$Content.Replace("MICROPHONE_ENABLED=False","MICROPHONE_ENABLED=True")
}
$Content=$Content.Replace('MICROPHONE_DEVICE="plughw:CARD=Microphone,DEV=0"','MICROPHONE_DEVICE="plughw:CARD=Device,DEV=0"')
$Content=$Content.Replace('MICROPHONE_DEVICE="hw:CARD=Device,DEV=0"','MICROPHONE_DEVICE="plughw:CARD=Device,DEV=0"')
Set-Content $Path $Content -Encoding utf8 -NoNewline

# app.py
$Path=".\robot\api\app.py"
$Content=Get-Content $Path -Raw
if ($Content -notmatch 'def microphone_status\(\):') {
    $Block=@'
def microphone_status():
    if not getattr(settings,"MICROPHONE_ENABLED",True):
        return {"enabled":False,"available":False,"device":settings.MICROPHONE_DEVICE}
    try:
        process=subprocess.run(["arecord","-l"],capture_output=True,text=True,timeout=3)
        output=(process.stdout or "")+"\n"+(process.stderr or "")
        available=process.returncode==0 and ("USB PnP Sound Device" in output or "USB Audio" in output)
        return {"enabled":True,"available":available,"device":settings.MICROPHONE_DEVICE,"model":"Texas Instruments PCM2902 / USB PnP Sound Device" if available else None}
    except Exception as error:
        return {"enabled":True,"available":False,"device":settings.MICROPHONE_DEVICE,"error":str(error)}

'@
    $Content=$Content.Replace("def thermal_status(robot):",$Block+"def thermal_status(robot):")
}

$Old=@'
@app.get("/audio/listen")
def audio_listen():
    return StreamingResponse(microphone_chunks(),media_type="audio/wav",headers={"Cache-Control":"no-store"})
'@
$New=@'
@app.get("/audio/microphone/status")
def audio_microphone_status():return microphone_status()

@app.get("/audio/listen")
def audio_listen():
    status=microphone_status()
    if not status.get("enabled"):raise HTTPException(status_code=503,detail="Microphone disabled")
    if not status.get("available"):raise HTTPException(status_code=503,detail="USB microphone unavailable")
    return StreamingResponse(microphone_chunks(),media_type="audio/wav",headers={"Cache-Control":"no-store"})
'@
if ($Content.Contains($Old)) {$Content=$Content.Replace($Old,$New)}
elseif ($Content -notmatch 'def audio_microphone_status\(\)') {throw "Could not patch /audio/listen in app.py"}

$Old='"speaker":robot.speaker is not None,"servo":robot.servo is not None,"shell":robot.shell is not None'
$New='"speaker":robot.speaker is not None,"microphone":microphone_status(),"servo":robot.servo is not None,"shell":robot.shell is not None'
if ($Content.Contains($Old)) {$Content=$Content.Replace($Old,$New)}
elseif ($Content -notmatch '"microphone":microphone_status\(\)') {throw "Could not add microphone health status"}
Set-Content $Path $Content -Encoding utf8 -NoNewline

# touch arrows -> ASCII
$Path=".\robot\shell\ui\touch_views.py"
$Content=Get-Content $Path -Raw
$Content=$Content.Replace('("←","back")','("<-","back")')
$Content=$Content.Replace('("←","◀","▶")','("<-","<<",">>")')
Set-Content $Path $Content -Encoding utf8 -NoNewline

# wiring.md
$Path=".\docs\wiring.md"
$Content=Get-Content $Path -Raw
if ($Content -notmatch 'Texas Instruments PCM2902') {
    $Old=@'
## USB Microphone

The microphone has an integrated USB audio interface and connects directly to a Raspberry Pi USB port. No GPIO connection is required.

Detection:

```bash
arecord -l
```
'@
    $New=@'
## USB Microphone

The microphone has an integrated USB audio interface and connects directly to a Raspberry Pi USB port. No GPIO connection is required.

Validated hardware:

- USB codec: Texas Instruments PCM2902 (`08bb:2902`)
- ALSA card: `Device` / `USB PnP Sound Device`
- Capture device: `plughw:CARD=Device,DEV=0`
- Runtime format: 16-bit PCM, 16 kHz, mono

Detection:

```bash
lsusb
arecord -l
```

Quick 5-second capture test:

```bash
arecord -D plughw:CARD=Device,DEV=0 -f S16_LE -r 16000 -c1 -d5 /tmp/mic-test.wav
aplay -D plughw:CARD=MAX98357A,DEV=0 /tmp/mic-test.wav
```
'@
    if (-not $Content.Contains($Old)) {throw "Could not find USB Microphone section in docs/wiring.md"}
    $Content=$Content.Replace($Old,$New)
}
Set-Content $Path $Content -Encoding utf8 -NoNewline

if (Test-Path ".\.venv\Scripts\python.exe") {$Python=".\.venv\Scripts\python.exe"}
elseif (Get-Command python -ErrorAction SilentlyContinue) {$Python="python"}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {$Python="python3"}
else {throw "No Python interpreter found."}

& $Python -m py_compile ".\robot\config\settings.py" ".\robot\api\app.py" ".\robot\shell\ui\touch_views.py"
if ($LASTEXITCODE -ne 0) {throw "Python syntax validation failed."}

Write-Host ""
Write-Host "Patch applied successfully." -ForegroundColor Green
Write-Host "- microphone enabled"
Write-Host "- device: plughw:CARD=Device,DEV=0"
Write-Host "- /audio/microphone/status added"
Write-Host "- /health includes microphone status"
Write-Host "- touchscreen arrows changed to <-  <<  >>"
Write-Host "- scripts/test_microphone.sh added"
Write-Host ""
git status --short
git diff --stat
