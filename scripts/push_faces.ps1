$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root "robot\assets\faces"
$remote = "spy@spyturtle.local"
$remotePath = "/home/spy/spy_turtle/robot/assets/faces"

if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw "Folder not found: $source" }

$folders = @(Get-ChildItem -LiteralPath $source -Directory)
$photos = @(Get-ChildItem -LiteralPath $source -Recurse -File | Where-Object { $_.Extension -in @(".jpg", ".jpeg", ".png", ".webp") })

Write-Host "Found $($photos.Count) photos in $($folders.Count) folders."

if ($photos.Count -eq 0) { throw "No photos found. Transfer cancelled." }

ssh -o ConnectTimeout=10 $remote "mkdir -p '$remotePath'"
if ($LASTEXITCODE -ne 0) { throw "SSH connection failed." }

foreach ($folder in $folders) {
    Write-Host "Uploading $($folder.Name)..."
    scp -r -o ConnectTimeout=10 -o ServerAliveInterval=15 -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 $folder.FullName "${remote}:$remotePath/"
    if ($LASTEXITCODE -ne 0) { throw "Transfer failed: $($folder.Name)" }
}

Write-Host "Transfer completed successfully."