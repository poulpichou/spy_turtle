$ErrorActionPreference = "Stop"
$Patch = Join-Path $PWD "spy_turtle_touch_ui"

if (-not (Test-Path ".\robot\shell\shell_controller.py") -or
    -not (Test-Path ".\robot\config\settings.py") -or
    -not (Test-Path ".\robot\system\robot.py")) {
    throw "Run this script from the root of the spy_turtle repository."
}
if (-not (Test-Path "$Patch\robot\hardware\touchscreen.py")) {
    throw "Patch folder not found at: $Patch"
}

Write-Host "Applying Spy Turtle touchscreen UI..." -ForegroundColor Cyan

Copy-Item "$Patch\robot\hardware\touchscreen.py" ".\robot\hardware\touchscreen.py" -Force
Copy-Item "$Patch\robot\shell\ui\touch_views.py" ".\robot\shell\ui\touch_views.py" -Force
Copy-Item "$Patch\robot\shell\touch_controller.py" ".\robot\shell\touch_controller.py" -Force
Copy-Item "$Patch\robot\shell\shell_controller.py" ".\robot\shell\shell_controller.py" -Force
Copy-Item "$Patch\scripts\test_touchscreen.py" ".\scripts\test_touchscreen.py" -Force

# Settings: enable CTP and add explicit geometry/orientation flags.
$SettingsPath=".\robot\config\settings.py"
$Settings=Get-Content $SettingsPath -Raw

if ($Settings -match 'ST7796_CTP_ENABLED=False') {
    $Settings=$Settings.Replace('ST7796_CTP_ENABLED=False','ST7796_CTP_ENABLED=True')
} elseif ($Settings -notmatch 'ST7796_CTP_ENABLED=True') {
    $Settings += "`nST7796_CTP_ENABLED=True`n"
}

if ($Settings -notmatch 'ST7796_CTP_WIDTH=') {
    $Marker='ST7796_CTP_RST_GPIO=23'
    $Block=@"
ST7796_CTP_RST_GPIO=23
ST7796_CTP_WIDTH=320
ST7796_CTP_HEIGHT=480
ST7796_CTP_SWAP_XY=False
ST7796_CTP_INVERT_X=False
ST7796_CTP_INVERT_Y=False
"@
    if ($Settings.Contains($Marker)) {$Settings=$Settings.Replace($Marker,$Block)}
    else {$Settings += "`n$Block"}
}
Set-Content -Path $SettingsPath -Value $Settings -Encoding utf8 -NoNewline

# Keep touchscreen polling alive while Idle mode has disabled the back screen.
$RobotPath=".\robot\system\robot.py"
$Robot=Get-Content $RobotPath -Raw
$Old=@"
        if self.power.idle_mode:
            self._update_battery(interval=self.IDLE_BATTERY_UPDATE_INTERVAL)
            return
"@
$New=@"
        if self.power.idle_mode:
            self._update_battery(interval=self.IDLE_BATTERY_UPDATE_INTERVAL)
            if self.shell and hasattr(self.shell,'update_touch_only'):self.shell.update_touch_only()
            return
"@
if ($Robot.Contains($Old)) {
    $Robot=$Robot.Replace($Old,$New)
} elseif (-not $Robot.Contains("hasattr(self.shell,'update_touch_only')")) {
    throw "Could not update idle touchscreen polling in robot/system/robot.py"
}
Set-Content -Path $RobotPath -Value $Robot -Encoding utf8 -NoNewline

# Syntax validation.
if (Test-Path ".\.venv\Scripts\python.exe") {$Python=".\.venv\Scripts\python.exe"}
elseif (Get-Command python -ErrorAction SilentlyContinue) {$Python="python"}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {$Python="python3"}
else {throw "No Python interpreter found."}

& $Python -m py_compile `
    ".\robot\hardware\touchscreen.py" `
    ".\robot\shell\ui\touch_views.py" `
    ".\robot\shell\touch_controller.py" `
    ".\robot\shell\shell_controller.py" `
    ".\scripts\test_touchscreen.py" `
    ".\robot\system\robot.py"
if ($LASTEXITCODE -ne 0) {throw "Python syntax validation failed."}

Write-Host ""
Write-Host "Touchscreen UI patch applied." -ForegroundColor Green
Write-Host ""
Write-Host "Before starting the full turtle, test touch detection on the Raspberry Pi:"
Write-Host "  python scripts/test_touchscreen.py"
Write-Host ""
git status --short
git diff --stat
