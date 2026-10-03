# Spy Turtle live Listen fix

The old Listen implementation streamed an endless WAV directly into an HTML `<audio>` element. Mobile Chrome can reject this because WAV normally expects a finite file/header length. The frontend error was then obscured by `pause()` being called while `play()` was still pending.

This patch:
- streams raw signed 16-bit little-endian PCM from `arecord`
- keeps the validated 16 kHz mono microphone format
- plays the stream in the browser with `AudioContext`
- uses `AbortController` to stop listening cleanly
- removes the old `<audio>.play()` / `.pause()` race

Apply from the root of `spy_turtle`:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\spy_turtle_live_listen_fix\apply_patch.ps1
```

Then:

```powershell
git diff
git add -A
git commit -m "Fix live microphone streaming"
git push
```

On the Pi:

```bash
cd ~/spy_turtle
git pull
source .venv/bin/activate
python -m robot.startup.main
```

Then reload the frontend on the phone and test the Listen toggle.
