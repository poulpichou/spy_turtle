# Spy Turtle Eyes V2

This package contains individual 128x64 `.eye` files and a complete `sequences.json`.

## Install from PowerShell

Run from the repository root:

```powershell
Get-ChildItem ".\spy_turtle_eyes_v2\robot\assets\eyes\*.eye" | Copy-Item -Destination ".\robot\assets\eyes" -Force
Copy-Item ".\spy_turtle_eyes_v2\robot\config\face\sequences.json" ".\robot\config\face\sequences.json" -Force
Copy-Item ".\spy_turtle_eyes_v2\update_assets.py" ".\update_assets.py" -Force
python .\update_assets.py
Remove-Item ".\update_assets.py"
```

The sequences include smooth blink, double blink, look left/right/high/down, yawn, wake up and sleeping.
