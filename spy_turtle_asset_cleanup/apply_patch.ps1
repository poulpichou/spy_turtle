$ErrorActionPreference = "Stop"
$Patch = Join-Path $PWD "spy_turtle_asset_cleanup"

if (-not (Test-Path ".\robot\assets") -or -not (Test-Path ".\robot\config") -or -not (Test-Path ".\frontend")) {
    throw "Run this script from the root of the spy_turtle repository."
}
if (-not (Test-Path $Patch)) { throw "Patch folder not found: $Patch" }

Write-Host "Applying asset/config cleanup..." -ForegroundColor Cyan

Copy-Item "$Patch\robot\assets\assets.py" ".\robot\assets\assets.py" -Force
Copy-Item "$Patch\robot\assets\assets.json" ".\robot\assets\assets.json" -Force
Copy-Item "$Patch\frontend\js\controls.js" ".\frontend\js\controls.js" -Force
Copy-Item "$Patch\scripts\cleanup_configs.py" ".\scripts\cleanup_configs.py" -Force

$AppPath=".\robot\api\app.py"
$App=Get-Content $AppPath -Raw
$Old='def get_available_assets():return {section:build_assets(section) for section in ("shell","eyes","leds","audio")}'
$New='def get_available_assets():return {section:build_assets(section) for section in ("shell","faces","leds","audio")}'
if ($App.Contains($Old)) {
    $App=$App.Replace($Old,$New)
    Set-Content -Path $AppPath -Value $App -Encoding utf8 -NoNewline
} elseif (-not $App.Contains($New)) {
    throw "Could not update /assets section list in robot/api/app.py"
}

Remove-Item ".\robot\config\face\eyes.json" -Force -ErrorAction SilentlyContinue
Remove-Item ".\robot\config\leds\modes.json" -Force -ErrorAction SilentlyContinue

if (Test-Path ".\.venv\Scripts\python.exe") {$Python=".\.venv\Scripts\python.exe"}
elseif (Get-Command python -ErrorAction SilentlyContinue) {$Python="python"}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {$Python="python3"}
else {throw "No Python interpreter found."}

& $Python ".\scripts\cleanup_configs.py"
if ($LASTEXITCODE -ne 0) {throw "Config cleanup/validation failed."}

& $Python -m py_compile ".\robot\assets\assets.py" ".\robot\api\app.py" ".\scripts\cleanup_configs.py"
if ($LASTEXITCODE -ne 0) {throw "Python syntax validation failed."}

Write-Host ""
Write-Host "Asset/config cleanup applied." -ForegroundColor Green
Write-Host "Images, sounds, eye files, fonts, face sequences and LED modes are now auto-discovered."
Write-Host ""
git status --short
git diff --stat
