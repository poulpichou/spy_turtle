$ErrorActionPreference="Stop"
if(!(Test-Path ".\\frontend\\index.html")){throw "Run this script from the root of the spy_turtle repository."}
$p=".\\frontend\\index.html"
$c=[System.IO.File]::ReadAllText((Resolve-Path $p),[System.Text.Encoding]::UTF8)
$cp1252=[System.Text.Encoding]::GetEncoding(1252)
$utf8=New-Object System.Text.UTF8Encoding($false)
$fixed=$utf8.GetString($cp1252.GetBytes($c))
$expected=@("▲","◀","▶","▼","🐢","🔊","🎙️","💬","📶","🔋","✨","↔️","👀","📷","🎧","×","·")
$missing=@(); foreach($s in $expected){if(-not $fixed.Contains($s)){$missing+=$s}}
if($missing.Count -gt 0){throw "UTF-8 repair sanity check failed. Missing: $($missing -join ' ')"}
if(-not $fixed.Contains('id="head-servo-status"')){throw "Head servo status addition is missing; refusing to overwrite."}
[System.IO.File]::WriteAllText((Resolve-Path $p),$fixed,$utf8)
Write-Host "Frontend UTF-8 repaired." -ForegroundColor Green
Write-Host "Emojis restored; Head servo Admin status preserved."
git diff -- frontend/index.html
