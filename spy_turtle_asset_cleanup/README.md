# Spy Turtle asset/config cleanup

This update makes the asset catalog file-system driven and compacts the configuration files.

Changes:
- all files in `robot/assets/images` are auto-discovered as shell assets
- all `.wav`/`.mp3` files in `robot/assets/sounds` are auto-discovered
- all `.eye` files are auto-discovered
- fonts are auto-discovered
- face sequences come from `robot/config/face/sequences.json`
- LED modes come from `robot/config/leds.json`
- frontend face/shell/LED/sound selectors are populated from `/assets`
- stale frontend sounds (`applause`, `laugh`, `rocket`) are no longer referenced; `fart1` remains
- obsolete `robot/config/face/eyes.json` is removed
- obsolete `robot/config/leds/modes.json` is removed
- `red` / `Red test` LED mode is removed
- orphan LED helper animations are pruned
- shell profiles without an existing image are pruned
- face eye references and LED links are validated
- JSON files are compacted, keeping small objects and scalar arrays inline where practical

Extract the ZIP directly inside `spy_turtle`, then from the root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_asset_cleanup\apply_patch.ps1
```

Review and commit:

```powershell
git diff
git add -A
git commit -m "Clean asset catalog and compact configs"
git push
```

The reusable validator/compactor stays in the repo:

```bash
python scripts/cleanup_configs.py
```
