# Spy Turtle center stability fix

This update fixes:

- layout shifts when switching Camera / Logs / Photos;
- Chrome Android losing the tab controls after repeated switches;
- the camera frame touching the bottom edge;
- oversized center tabs.

The views now stay stacked in a fixed-size container and are switched with visibility, opacity and pointer-events instead of display changes.

## PowerShell installation

```powershell
Copy-Item ".\spy_turtle_center_stability_fix\frontend\css\style.css" ".\frontend\css\style.css" -Force
Copy-Item ".\spy_turtle_center_stability_fix\frontend\css\mobile.css" ".\frontend\css\mobile.css" -Force
Copy-Item ".\spy_turtle_center_stability_fix\frontend\js\center.js" ".\frontend\js\center.js" -Force
```

Then increase the cache version in `frontend/service-worker.js`, for example:

```javascript
const CACHE_NAME="spy-turtle-v2";
```

Commit, deploy, close the PWA completely and reopen it.
