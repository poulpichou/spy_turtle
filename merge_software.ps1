param([string]$RepoRoot=".")
$ErrorActionPreference="Stop"
$root=(Resolve-Path $RepoRoot).Path
$docs=Join-Path $root "docs"

function Read-Utf8([string]$Path){
    if(-not (Test-Path $Path)){throw "Missing source file: $Path"}
    [System.IO.File]::ReadAllText($Path,[System.Text.Encoding]::UTF8)
}
function Write-Utf8NoBom([string]$Path,[string]$Content){
    $encoding=New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path,$Content,$encoding)
}
function Metrics([string]$Text){
    $normalized=$Text -replace "`r`n","`n"
    $lines=if($normalized.Length -eq 0){0}else{($normalized -split "`n").Count}
    [ordered]@{
        lines=$lines
        characters=$Text.Length
        bytes_utf8=[System.Text.Encoding]::UTF8.GetByteCount($Text)
    }
}
function Slug([string]$Title){
    $value=$Title.ToLowerInvariant()
    $value=$value -replace '[`*_~\[\]\(\):/\\]',''
    $value=$value -replace '[^a-z0-9\s-]',''
    $value=$value.Trim() -replace '\s+','-'
    $value=$value -replace '-+','-'
    $value
}
function NaturalKey([string]$Name){
    [regex]::Replace($Name,'\d+',{$args[0].Value.PadLeft(10,'0')})
}

$patterns=@("software*.md","api*.md","deployment*.md")
$files=@()
foreach($pattern in $patterns){
    $files+=Get-ChildItem -Path $docs -File -Filter $pattern
}
$files=$files |
    Where-Object {$_.Name -notin @("software_merged.md")} |
    Sort-Object @{Expression={NaturalKey $_.Name}} -Unique

if($files.Count -eq 0){
    throw "No software/API/deployment Markdown files found in docs/"
}

$texts=@()
foreach($file in $files){$texts+=Read-Utf8 $file.FullName}
$base=($texts | ForEach-Object {($_ -replace "`r`n","`n").Trim("`r","`n")}) -join "`n`n"

$headings=@()
$seen=@{}
foreach($line in ($base -split "`n")){
    if($line -match '^(#{1,2})\s+(.+?)\s*$'){
        $level=$matches[1].Length
        $title=$matches[2].Trim()
        if($title -match '^Table of contents$'){continue}
        $slug=Slug $title
        if(-not $slug){continue}
        if($seen.ContainsKey($slug)){
            $seen[$slug]++
            $slug="$slug-$($seen[$slug])"
        }else{$seen[$slug]=0}
        $headings+=[ordered]@{level=$level;title=$title;slug=$slug}
    }
}
$tocLines=@("## Table of contents")
foreach($heading in $headings){
    $indent=if($heading.level -eq 1){""}else{"  "}
    $tocLines+="$indent- [$($heading.title)](#$($heading.slug))"
}
$toc=$tocLines -join "`n"

$firstLineEnd=$base.IndexOf("`n")
if($firstLineEnd -ge 0 -and $base.Substring(0,$firstLineEnd) -match '^#\s+'){
    $merged=$base.Substring(0,$firstLineEnd)+"`n`n"+$toc+"`n`n"+$base.Substring($firstLineEnd+1).TrimStart("`n")
}else{
    $merged="# Software`n`n"+$toc+"`n`n"+$base
}

$tocBlock="`n`n"+$toc+"`n`n"
$withoutToc=$merged.Replace($tocBlock,"`n`n")
if($withoutToc.StartsWith("# Software`n`n") -and -not $base.StartsWith("# ")){
    $withoutToc=$withoutToc.Substring(12)
}
$verified=($withoutToc -eq $base)
if(-not $verified){throw "Verification failed: source content changed"}

$destination=Join-Path $docs "software_merged.md"
Write-Utf8NoBom $destination $merged

$before=@()
foreach($i in 0..($files.Count-1)){
    $before+=[ordered]@{file=$files[$i].Name;metrics=Metrics $texts[$i]}
}
$beforeLines=($before|ForEach-Object{$_.metrics.lines}|Measure-Object -Sum).Sum
$beforeChars=($before|ForEach-Object{$_.metrics.characters}|Measure-Object -Sum).Sum
$beforeBytes=($before|ForEach-Object{$_.metrics.bytes_utf8}|Measure-Object -Sum).Sum
$after=Metrics $merged
$report=[ordered]@{
    sources=$before
    before_total=[ordered]@{lines=$beforeLines;characters=$beforeChars;bytes_utf8=$beforeBytes}
    destination=[ordered]@{file="software_merged.md";metrics=$after}
    difference=[ordered]@{
        lines=$after.lines-$beforeLines
        characters=$after.characters-$beforeChars
        bytes_utf8=$after.bytes_utf8-$beforeBytes
    }
    source_content_preserved_in_order=$verified
    note="Output is software_merged.md to avoid overwriting any existing software.md before review."
}
Write-Utf8NoBom (Join-Path $root "SOFTWARE_MERGE_REPORT.json") ($report|ConvertTo-Json -Depth 8)

$lines=@(
    "# Software Merge Report","",
    "| File | Lines | Characters | UTF-8 bytes |",
    "|---|---:|---:|---:|"
)
foreach($source in $before){
    $m=$source.metrics
    $lines+="| ``$($source.file)`` | $($m.lines) | $($m.characters) | $($m.bytes_utf8) |"
}
$lines+="| **Before total** | **$beforeLines** | **$beforeChars** | **$beforeBytes** |"
$lines+="| ``software_merged.md`` | **$($after.lines)** | **$($after.characters)** | **$($after.bytes_utf8)** |"
$lines+="| **Difference** | **$($report.difference.lines)** | **$($report.difference.characters)** | **$($report.difference.bytes_utf8)** |"
$lines+=""
$lines+="Source content preserved in order: **$verified**"
$lines+=""
$lines+="Sources discovered: **$($files.Name -join ', ')**"
Write-Utf8NoBom (Join-Path $root "SOFTWARE_MERGE_REPORT.md") ($lines -join "`n")

Write-Host "Created docs/software_merged.md"
Write-Host "Sources: $($files.Name -join ', ')"
Write-Host "Verification passed: $verified"
Write-Host "Review SOFTWARE_MERGE_REPORT.md and git diff before renaming or deleting anything."
