$ErrorActionPreference = "Stop"
$Patch = Join-Path $PWD "spy_turtle_asset_cleanup_fix"

if (-not (Test-Path ".\robot\config\leds.json") -or -not (Test-Path ".\scripts\cleanup_configs.py")) {
    throw "Run this script from the root of spy_turtle, after the first asset cleanup patch failed."
}
if (-not (Test-Path $Patch)) { throw "Patch folder not found: $Patch" }

if (Test-Path ".\.venv\Scripts\python.exe") {$Python=".\.venv\Scripts\python.exe"}
elseif (Get-Command python -ErrorAction SilentlyContinue) {$Python="python"}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {$Python="python3"}
else {throw "No Python interpreter found."}

Write-Host "Fixing missing face-linked LED modes..." -ForegroundColor Cyan
& $Python "$Patch\scripts\fix_asset_cleanup.py"
if ($LASTEXITCODE -ne 0) {throw "Unable to repair robot/config/leds.json."}

Write-Host "Re-running asset/config cleanup and validation..." -ForegroundColor Cyan
& $Python ".\scripts\cleanup_configs.py"
if ($LASTEXITCODE -ne 0) {throw "Config cleanup/validation still failed."}

& $Python -m py_compile ".\robot\assets\assets.py" ".\robot\api\app.py" ".\scripts\cleanup_configs.py"
if ($LASTEXITCODE -ne 0) {throw "Python syntax validation failed."}

Write-Host ""
Write-Host "Asset cleanup completed successfully." -ForegroundColor Green
Write-Host ""
git status --short
git diff --stat
