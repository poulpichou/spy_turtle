# Frontend and camera cleanup

This update replaces the duplicated files created by repeatedly applying the previous patch.

Changes:
- one API router, middleware, `/version`, `/health` HTTPS entry, Thermal route and Admin view
- exactly six center tabs
- no frontend/service-worker cache
- Picamera2 recreation after a broken start or capture pipe
- synchronized RGB/Thermal fallback access

After deployment, close the installed Chrome app completely and open it again once. The old service worker will unregister itself and all application caches will be deleted.
