$ErrorActionPreference = "Stop"
$Patch = Join-Path $PWD "spy_turtle_eyes_optional"

if (-not (Test-Path ".\robot\config\settings.py") -or -not (Test-Path ".\robot\factory\robot_factory.py")) {
    throw "Run this script from the root of the spy_turtle repository."
}
if (-not (Test-Path "$Patch\scripts\apply_eyes_optional.py")) {
    throw "Patch folder not found at: $Patch"
}

if (Test-Path ".\.venv\Scripts\python.exe") {$Python=".\.venv\Scripts\python.exe"}
elseif (Get-Command python -ErrorAction SilentlyContinue) {$Python="python"}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {$Python="python3"}
else {throw "No Python interpreter found."}

Write-Host "Applying optional OLED eyes support..." -ForegroundColor Cyan

Copy-Item "$Patch\robot\hardware\null_eyes_display.py" ".\robot\hardware\null_eyes_display.py" -Force

& $Python "$Patch\scripts\apply_eyes_optional.py"
if ($LASTEXITCODE -ne 0) {throw "Unable to patch OLED eye configuration."}

& $Python -m py_compile `
    ".\robot\hardware\null_eyes_display.py" `
    ".\robot\factory\robot_factory.py" `
    ".\robot\config\settings.py"
if ($LASTEXITCODE -ne 0) {throw "Python syntax validation failed."}

Write-Host ""
Write-Host "Patch applied successfully." -ForegroundColor Green
Write-Host "OLED eyes are currently DISABLED: EYES_ENABLED=False" -ForegroundColor Yellow
Write-Host "Set EYES_ENABLED=True later to re-enable them."
Write-Host "If an OLED is missing at startup while enabled, Spy Turtle will continue without eyes."
Write-Host ""
git status --short
git diff --stat
