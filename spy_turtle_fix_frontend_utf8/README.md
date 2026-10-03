# Spy Turtle frontend UTF-8 repair

Repairs the mojibake in `frontend/index.html` while preserving the Head servo Admin addition.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_fix_frontend_utf8\apply_patch.ps1
```

Then:

```powershell
git diff
git add frontend/index.html
git commit -m "Fix frontend UTF-8 encoding"
git push
```

On the Turtle:

```bash
cd ~/spy_turtle
git pull
```

Hard-refresh/reload the PWA on the phone afterward.
