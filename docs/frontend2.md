# POST Endpoints

## POST /move

```json
{
    "direction":"forward"
}
```

Accepted values:

* forward
* backward
* left
* right
* stop

---

## POST /head

```json
{
    "direction":"left"
}
```

Accepted values:

* left
* right
* up
* down
* center

---

## POST /face

```json
{
    "face":"happy"
}
```

---

## POST /led

```json
{
    "mode":"rainbow"
}
```

---

## POST /sound

```json
{
    "sound":"startup"
}
```

---

## POST /message

```json
{
    "text":"Hello!"
}
```

---

## POST /photo

Triggers a snapshot.

Returns:

```json
{
    "filename":"photo_0007.jpg"
}
```

---

# Refresh Strategy

Status:

* Refresh every second.

Camera:

* Continuous MJPEG stream.

Movement:

* Commands sent immediately while buttons are pressed.

Head:

* Commands sent immediately while buttons are pressed.

---

# Future WebSocket API

A future version will maintain a permanent WebSocket connection.

The robot will push events automatically:

* battery updates
* emotion changes
* LED mode changes
* WiFi status
* warnings
* notifications
* camera statistics

This will replace periodic polling.

---

# Frontend Directory Structure

```text
frontend/

    index.html

    css/
        style.css
        mobile.css

    js/
        api.js
        camera.js
        controls.js
        dashboard.js
        ui.js

    assets/
        icons/
        sounds/
```

---

# JavaScript Responsibilities

## api.js

Handles all REST communication.

---

## camera.js

Displays the camera stream.

---

## controls.js

Handles:

* movement controls
* head controls
* touch events
* keyboard shortcuts (desktop)

---

## dashboard.js

Updates:

* battery
* WiFi
* emotion
* LED mode
* robot status

---

## ui.js

Handles:

* dropdown menus
* buttons
* notifications
* interface animations

---

# Current PWA and HTTPS Implementation
The frontend is served by the robot and installed from the browser as a standalone PWA. Caddy terminates HTTPS locally, which allows service-worker registration and removes the normal browser navigation bar when launched from the home screen.

Main PWA files include the web manifest, service worker, application icons and the existing frontend assets. The interface remains fully usable as a normal webpage when it is not installed.

---

# Current Control Integration
The frontend reads available eyes, LED modes, sounds and shell media from configuration-backed API data where possible. This avoids duplicating option lists in HTML and allows new assets or modes to appear without redesigning the interface.

Current controls include:
- Robot movement with press/hold/release handling.
- Head pan/tilt targets and center control.
- Eye/emotion sequence selection.
- LED mode selection, including expressive and directional effects.
- Sound selection.
- Shell message and media commands.
- Status information including battery, camera, LED mode, expression and servo current/target angles.

The shell Status view and frontend Status panel should expose the same essential state. Temporary shell modes may also coordinate matching eye and LED behavior.

---

# Compact Smartphone Controls
Native mobile dropdowns were replaced where necessary with custom compact dropdown controls so their opened and closed sizes remain consistent with the narrow side columns. The central panel can evolve into a switchable area for camera, logs and photo gallery while continuing to prioritize the live camera.

---

# Error Handling

If the robot becomes unreachable:

* movement buttons are disabled
* camera freezes
* a red warning banner appears
* automatic reconnection begins

If the camera stream is interrupted:

* display a placeholder image
* continue accepting movement commands

---

# Design Rules

The frontend should always remain:

* simple
* fast
* readable
* responsive
* mobile-first
* usable with two thumbs
* framework-free whenever possible

The frontend must never contain robot behaviour.

All intelligence belongs inside the Brain.

The frontend should remain sufficiently generic so that the same backend could later support:

* another web interface
* a desktop interface
* a native mobile application

without changing the Brain itself.
