# Spy Turtle asset cleanup fix v2

The previous fix had a path bug: its Python helper resolved the patch folder as the repository root, so it looked for:

```text
spy_turtle_asset_cleanup_fix/robot/config/leds.json
```

instead of:

```text
spy_turtle/robot/config/leds.json
```

This version deliberately uses the current working directory as the repository root.

Do not revert the partially applied first asset cleanup patch.

Extract this ZIP directly inside `spy_turtle`, then from the root of `spy_turtle` run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_asset_cleanup_fix_v2\apply_patch.ps1
```

Then:

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
