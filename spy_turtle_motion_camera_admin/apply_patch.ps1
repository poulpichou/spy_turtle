$ErrorActionPreference="Stop"
$utf8=New-Object System.Text.UTF8Encoding($false)
function ReadUtf8($p){return [System.IO.File]::ReadAllText((Resolve-Path $p),[System.Text.Encoding]::UTF8)}
function WriteUtf8($p,$c){[System.IO.File]::WriteAllText((Resolve-Path $p),$c,$utf8)}
function ReplaceRequired($c,$old,$new,$label){if(-not $c.Contains($old)){throw "Could not find expected text: $label"};return $c.Replace($old,$new)}

if(!(Test-Path ".\robot\config\servos.json") -or !(Test-Path ".\frontend\index.html")){throw "Run from the spy_turtle repository root."}

# 1) Servo amplitude: PAN remains 150 total; TILT becomes 120 total.
$p=".\robot\config\servos.json";$c=ReadUtf8 $p
$c=ReplaceRequired $c '"minimum_angle_deg": -45.0, "maximum_angle_deg": 45.0' '"minimum_angle_deg": -60.0, "maximum_angle_deg": 60.0' "tilt limits"
WriteUtf8 $p $c

# 2) Runtime motor speed multiplier. 100% = current speed, 300% = x3, capped by motor max.
$p=".\robot\hardware\motor\differential_drive.py";$c=ReadUtf8 $p
$c=ReplaceRequired $c '        self.motion="stop"' "        self.motion=`"stop`"`n        self.speed_multiplier=1.0" "motor init"
$c=ReplaceRequired $c '    def forward(self,speed=None):' "    def set_speed_percent(self,percent):`n        self.speed_multiplier=max(1.0,min(3.0,float(percent)/100.0))`n        return round(self.speed_multiplier*100)`n`n    def get_speed_percent(self): return round(self.speed_multiplier*100)`n`n    def forward(self,speed=None):" "motor speed methods"
$c=ReplaceRequired $c '        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED)' '        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED*self.speed_multiplier)' "forward speed"
$c=ReplaceRequired $c '        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED)' '        speed=self.normalize_speed(speed,settings.MOTOR_DRIVE_SPEED*self.speed_multiplier)' "backward speed"
$c=ReplaceRequired $c '        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED)' '        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED*self.speed_multiplier)' "left speed"
$c=ReplaceRequired $c '        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED)' '        speed=self.normalize_speed(speed,settings.MOTOR_TURN_SPEED*self.speed_multiplier)' "right speed"
WriteUtf8 $p $c

# 3) Admin API for motor speed.
$p=".\robot\api\admin.py";$c=ReadUtf8 $p
$c=ReplaceRequired $c 'class SensitivityRequest(BaseModel): sensitivity:int=Field(ge=0,le=100)' "class SensitivityRequest(BaseModel): sensitivity:int=Field(ge=0,le=100)`nclass MotorSpeedRequest(BaseModel): speed:int=Field(ge=100,le=300)" "speed request model"
$api=@'

@router.get('/motors/speed')
def get_motor_speed():
    robot=robot_or_503()
    if robot.motors is None or not hasattr(robot.motors,'get_speed_percent'):raise HTTPException(status_code=503,detail='Motor speed control unavailable')
    return {'ok':True,'speed':robot.motors.get_speed_percent()}
@router.post('/motors/speed')
def set_motor_speed(data:MotorSpeedRequest,request:Request):
    robot=robot_or_503()
    if robot.motors is None or not hasattr(robot.motors,'set_speed_percent'):raise HTTPException(status_code=503,detail='Motor speed control unavailable')
    speed=robot.motors.set_speed_percent(data.speed)
    log.info(f'[ADMIN] motor speed={speed}% {source(request)}')
    return {'ok':True,'speed':speed,'message':f'Drive speed set to {speed}%'}
'@
$c += $api
WriteUtf8 $p $c

# 4) Admin HTML: remove servo debug line; add Drive speed + Camera FPS.
$p=".\frontend\index.html";$c=ReadUtf8 $p
$c=$c.Replace('<pre id="head-servo-status">Head servos: loading...</pre>','')
$micro='<div class="admin-slider"><label>Micro sensitivity <strong id="micro-value">60%</strong></label><input id="micro-slider" type="range" min="0" max="100" value="60"></div>'
$extra=$micro+'<div class="admin-slider"><label>Drive speed <strong id="drive-speed-value">100%</strong></label><input id="drive-speed-slider" type="range" min="100" max="300" step="10" value="100"></div><div class="admin-slider"><label>Camera <strong id="camera-fps-value">6 fps</strong></label><input id="camera-fps-slider" type="range" min="2" max="10" step="1" value="6"></div>'
$c=ReplaceRequired $c $micro $extra "Admin sliders"
WriteUtf8 $p $c

# 5) Camera refresh is locally adjustable and persisted in the browser.
$p=".\frontend\js\camera.js"
$c='const camera=document.getElementById("camera-stream");let cameraTimer=null;let cameraFps=Math.max(2,Math.min(10,Number(localStorage.getItem("spy_turtle_camera_fps"))||6));function updateCamera(){if(!document.getElementById("camera-view").classList.contains("active"))return;camera.src="/camera/frame?t="+Date.now()}function startCameraRefresh(){if(cameraTimer)return;updateCamera();cameraTimer=setInterval(updateCamera,Math.round(1000/cameraFps))}function stopCameraRefresh(){if(!cameraTimer)return;clearInterval(cameraTimer);cameraTimer=null}function setCameraFps(fps){cameraFps=Math.max(2,Math.min(10,Number(fps)||6));localStorage.setItem("spy_turtle_camera_fps",String(cameraFps));const running=!!cameraTimer;if(running){stopCameraRefresh();startCameraRefresh()}return cameraFps}function getCameraFps(){return cameraFps}startCameraRefresh();'
WriteUtf8 $p $c

# 6) Admin JS: remove old servo polling and add both sliders.
$p=".\frontend\js\admin.js";$c=ReadUtf8 $p
$c=ReplaceRequired $c 'const microSlider=document.getElementById("micro-slider"),microValue=document.getElementById("micro-value");' 'const microSlider=document.getElementById("micro-slider"),microValue=document.getElementById("micro-value");const driveSpeedSlider=document.getElementById("drive-speed-slider"),driveSpeedValue=document.getElementById("drive-speed-value");const cameraFpsSlider=document.getElementById("camera-fps-slider"),cameraFpsValue=document.getElementById("camera-fps-value");' "admin slider constants"
$c=ReplaceRequired $c 'function showMicro(value){microValue.textContent=`${value}%`}' 'function showMicro(value){microValue.textContent=`${value}%`}function showDriveSpeed(value){driveSpeedValue.textContent=`${value}%`}function showCameraFps(value){cameraFpsValue.textContent=`${value} fps`}' "admin display functions"
$c=ReplaceRequired $c 'async function loadVolume(){try{const data=await adminGet("/admin/audio/volume");volumeSlider.value=data.volume;showVolume(data.volume)}catch(error){console.error("[VOLUME]",error)}}' 'async function loadVolume(){try{const data=await adminGet("/admin/audio/volume");volumeSlider.value=data.volume;showVolume(data.volume)}catch(error){console.error("[VOLUME]",error)}}async function loadDriveSpeed(){try{const data=await adminGet("/admin/motors/speed");driveSpeedSlider.value=data.speed;showDriveSpeed(data.speed)}catch(error){console.error("[MOTOR SPEED]",error)}}function loadCameraFps(){const fps=getCameraFps();cameraFpsSlider.value=fps;showCameraFps(fps)}' "admin loaders"
$c=ReplaceRequired $c 'microSlider.onchange=async()=>{try{const data=await adminPost("/admin/audio/microphone-sensitivity",{sensitivity:Number(microSlider.value)});applyPowerState(data);adminResult.textContent="Micro sensitivity saved"}catch(error){adminResult.textContent=error.message}};' 'microSlider.onchange=async()=>{try{const data=await adminPost("/admin/audio/microphone-sensitivity",{sensitivity:Number(microSlider.value)});applyPowerState(data);adminResult.textContent="Micro sensitivity saved"}catch(error){adminResult.textContent=error.message}};driveSpeedSlider.oninput=()=>showDriveSpeed(driveSpeedSlider.value);driveSpeedSlider.onchange=async()=>{try{const data=await adminPost("/admin/motors/speed",{speed:Number(driveSpeedSlider.value)});driveSpeedSlider.value=data.speed;showDriveSpeed(data.speed);adminResult.textContent=data.message}catch(error){adminResult.textContent=error.message}};cameraFpsSlider.oninput=()=>showCameraFps(cameraFpsSlider.value);cameraFpsSlider.onchange=()=>{const fps=setCameraFps(cameraFpsSlider.value);showCameraFps(fps);adminResult.textContent=`Camera refresh set to ${fps} fps`};' "admin slider handlers"
$c=$c.Replace(',loadHeadServoStatus()','')
$marker='async function loadHeadServoStatus(){'
$i=$c.IndexOf($marker)
if($i -ge 0){$c=$c.Substring(0,$i).TrimEnd()+"`n"}
$c=$c.Replace('await Promise.allSettled([loadPower(),loadVolume(),loadWifi()])','await Promise.allSettled([loadPower(),loadVolume(),loadDriveSpeed(),loadWifi()]);loadCameraFps()')
$c=$c.Replace('await Promise.allSettled([loadVolume(),loadPower(),loadWifi()])','await Promise.allSettled([loadVolume(),loadPower(),loadDriveSpeed(),loadWifi()]);loadCameraFps()')
WriteUtf8 $p $c

# Validate without re-encoding files.
if(Test-Path ".\.venv\Scripts\python.exe"){$py=".\.venv\Scripts\python.exe"}elseif(Get-Command python -ErrorAction SilentlyContinue){$py="python"}else{$py="python3"}
& $py -m py_compile ".\robot\api\admin.py" ".\robot\hardware\motor\differential_drive.py"
if($LASTEXITCODE -ne 0){throw "Python syntax validation failed."}

Write-Host "Patch applied." -ForegroundColor Green
Write-Host "- PAN: -75..+75 deg (150 total)"
Write-Host "- TILT: -60..+60 deg (120 total)"
Write-Host "- Removed Head servo debug line from web Admin"
Write-Host "- Added Drive speed 100..300% (100% = existing speed)"
Write-Host "- Added Camera FPS 2..10 (default 6)"
Write-Host ""
git diff --stat
