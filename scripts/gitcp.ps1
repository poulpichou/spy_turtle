param(
    [string]$Message = "fix"
)

if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = "fix"
}

git commit -a -m $Message

if ($LASTEXITCODE -ne 0) {
    Write-Host "Git commit failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

git push

if ($LASTEXITCODE -ne 0) {
    Write-Host "Git push failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Commit and push done: $Message" -ForegroundColor Green