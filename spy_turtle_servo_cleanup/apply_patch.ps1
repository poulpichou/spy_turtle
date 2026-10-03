$ErrorActionPreference="Stop"
$Patch=Join-Path $PWD "spy_turtle_servo_cleanup"

if(!(Test-Path ".\robot\config\servos.json") -or !(Test-Path ".\robot\hardware\servo.py") -or !(Test-Path ".\robot\config\settings.py")){
    throw "Run this script from the root of the spy_turtle repository."
}
if(!(Test-Path "$Patch\robot\config\servos.json")){throw "Patch folder not found: $Patch"}

Write-Host "Applying servo cleanup..." -ForegroundColor Cyan

Copy-Item "$Patch\robot\config\servos.json" ".\robot\config\servos.json" -Force
Copy-Item "$Patch\robot\hardware\servo.py" ".\robot\hardware\servo.py" -Force

# Re-enable OLED eyes.
$p=".\robot\config\settings.py"
$c=Get-Content $p -Raw
$c=$c.Replace("EYES_ENABLED=False","EYES_ENABLED=True")
Set-Content $p $c -Encoding utf8 -NoNewline

# Add HEAD INFO view to touchscreen Admin.
$p=".\robot\shell\ui\touch_views.py"
$c=Get-Content $p -Raw
$c=$c.Replace('items=[("WI-FI","wifi"),("IDLE","idle"),("SHUTDOWN","shutdown"),("<-","back")]','items=[("WI-FI","wifi"),("HEAD INFO","head_info"),("IDLE","idle"),("SHUTDOWN","shutdown"),("<-","back")]')
if($c -notmatch 'class HeadInfoView'){
$block=@'

class HeadInfoView(TouchView):
    footer="HEAD"
    def get_data(self,robot): return robot.servo.status() if robot.servo else {}
    def draw(self,draw,display,data):
        draw_title(draw,"HEAD SERVOS")
        pan=data.get("pan",{});tilt=data.get("tilt",{})
        text(draw,12,theme.CONTENT_Y+55,f"PAN  {pan.get('current','--')} deg -> {pan.get('target','--')} deg",15,colors.WHITE,True)
        text(draw,12,theme.CONTENT_Y+83,f"Pulse {pan.get('pulse_us','--')} us   center {pan.get('center_pulse_us','--')} us",13,colors.GRAY)
        text(draw,12,theme.CONTENT_Y+112,f"Range {pan.get('minimum','--')} .. {pan.get('maximum','--')} deg",13,colors.GRAY)
        text(draw,12,theme.CONTENT_Y+165,f"TILT {tilt.get('current','--')} deg -> {tilt.get('target','--')} deg",15,colors.WHITE,True)
        text(draw,12,theme.CONTENT_Y+193,f"Pulse {tilt.get('pulse_us','--')} us   center {tilt.get('center_pulse_us','--')} us",13,colors.GRAY)
        text(draw,12,theme.CONTENT_Y+222,f"Range {tilt.get('minimum','--')} .. {tilt.get('maximum','--')} deg",13,colors.GRAY)
        self.back=(ROW_X,theme.CONTENT_Y+285,ROW_X+ROW_W,theme.CONTENT_Y+337)
        draw_button(draw,self.back,"<-")
    def action_at(self,x,y):
        if inside(x,y,self.back):return "back"
'@
$c=$c.Replace("class WifiView(TouchView):",$block+"`r`nclass WifiView(TouchView):")
}
Set-Content $p $c -Encoding utf8 -NoNewline

# Wire HeadInfoView into touch controller.
$p=".\robot\shell\touch_controller.py"
$c=Get-Content $p -Raw
$c=$c.Replace("from robot.shell.ui.touch_views import HomeView,CommandsView,SelectionView,AdminView,WifiView,ConfirmShutdownView","from robot.shell.ui.touch_views import HomeView,CommandsView,SelectionView,AdminView,HeadInfoView,WifiView,ConfirmShutdownView")
$c=$c.Replace('if action=="admin":self._show(AdminView(),"touch_admin");return','if action=="admin":self._show(AdminView(),"touch_admin");return'+"`r`n        "+'if action=="head_info":self._show(HeadInfoView(),"touch_head_info");return')
$c=$c.Replace('if isinstance(view,(CommandsView,AdminView)):self.open_home()','if isinstance(view,(CommandsView,AdminView)):self.open_home()'+"`r`n            "+'elif isinstance(view,HeadInfoView):self._show(AdminView(),"touch_admin")')
Set-Content $p $c -Encoding utf8 -NoNewline

# Add live head info to web Admin.
$p=".\frontend\index.html"
$c=Get-Content $p -Raw
if($c -notmatch 'id="head-servo-status"'){
    $needle='<div class="admin-slider"><label>Micro sensitivity <strong id="micro-value">60%</strong></label><input id="micro-slider" type="range" min="0" max="100" value="60"></div>'
    $replace=$needle+'<pre id="head-servo-status">Head servos: loading...</pre>'
    if(-not $c.Contains($needle)){throw "Could not find Admin microphone slider in frontend/index.html"}
    $c=$c.Replace($needle,$replace)
}
Set-Content $p $c -Encoding utf8 -NoNewline

$p=".\frontend\js\admin.js"
$c=Get-Content $p -Raw
if($c -notmatch 'function loadHeadServoStatus'){
$insert=@'

async function loadHeadServoStatus(){
    const output=document.getElementById("head-servo-status");if(!output)return;
    try{
        const response=await fetch(`/state?t=${Date.now()}`,{cache:"no-store"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const servo=(await response.json()).servo;
        if(!servo){output.textContent="Head servos unavailable";return}
        const line=axis=>`${axis.current}deg -> ${axis.target}deg | ${axis.pulse_us??"--"}us | center ${axis.center_pulse_us??"--"}us | range ${axis.minimum}..${axis.maximum}deg`;
        output.textContent=`PAN  ${line(servo.pan)}\nTILT ${line(servo.tilt)}`;
    }catch(error){output.textContent=`Head servos: ${error.message}`}
}
setInterval(loadHeadServoStatus,1500);
'@
$c += $insert
}
$c=$c.Replace('await Promise.allSettled([loadVolume(),loadPower(),loadWifi()])','await Promise.allSettled([loadVolume(),loadPower(),loadWifi(),loadHeadServoStatus()])')
Set-Content $p $c -Encoding utf8 -NoNewline

if(Test-Path ".\.venv\Scripts\python.exe"){$py=".\.venv\Scripts\python.exe"}elseif(Get-Command python -ErrorAction SilentlyContinue){$py="python"}else{$py="python3"}
& $py -m py_compile ".\robot\hardware\servo.py" ".\robot\shell\ui\touch_views.py" ".\robot\shell\touch_controller.py" ".\robot\config\settings.py"
if($LASTEXITCODE -ne 0){throw "Python syntax validation failed."}

Write-Host ""
Write-Host "Servo cleanup applied." -ForegroundColor Green
Write-Host "- PAN: -75 .. +75 degrees"
Write-Host "- TILT: -45 .. +45 degrees"
Write-Host "- PAN center pulse: 1500 us"
Write-Host "- TILT center pulse: 1500 us"
Write-Host "- OLED eyes re-enabled"
Write-Host "- Head servo info added to touchscreen Admin and web Admin"
Write-Host ""
Write-Host "IMPORTANT: TILT center changes from 1650 us to 1500 us." -ForegroundColor Yellow
Write-Host "Before the first robot start, loosen/remove the head linkage, let servos center, then mechanically align and reattach the head." -ForegroundColor Yellow
Write-Host ""
git status --short
git diff --stat
