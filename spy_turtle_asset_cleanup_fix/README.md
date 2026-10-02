# Spy Turtle asset cleanup fix

The first cleanup patch correctly detected a real inconsistency:

- face sequence `dizzy` references LED mode `dizzy`
- face sequence `thinking` references LED mode `thinking`
- both modes existed in the old legacy `robot/config/leds/modes.json`
- neither existed in the active runtime `robot/config/leds.json`

This fix adds both runtime LED modes and their animations, then resumes the cleanup/validation.

Do **not** revert the partially applied first patch.

Extract this ZIP directly inside the root of `spy_turtle`, then run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_asset_cleanup_fix\apply_patch.ps1
```

Then review:

```powershell
git diff
git status
```

If everything looks good:

```powershell
git add -A
git commit -m "Clean asset catalog and compact configs"
git push
```
