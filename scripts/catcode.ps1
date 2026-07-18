param(
    [string]$Dir
)

if (!$Dir) {
    Write-Host "Usage: .\catcode.ps1 <directory>"
    exit
}

$out="out.txt"
$extensions=@("*.py","*.js","*.html","*.css","*.json")

"" | Out-File $out

Get-ChildItem $Dir -Recurse -File |
Where-Object {
    ($extensions -contains ("*" + $_.Extension)) -and
    $_.FullName -notmatch "__pycache__" -and
    $_.FullName -notmatch ".venv" -and
    $_.FullName -notmatch "node_modules"
} |
Sort-Object FullName |
ForEach-Object {

    "========================================" | Out-File $out -Append
    $_.FullName | Out-File $out -Append
    "========================================" | Out-File $out -Append

    Get-Content $_.FullName | Out-File $out -Append

    "" | Out-File $out -Append
}

Write-Host "Created $out"