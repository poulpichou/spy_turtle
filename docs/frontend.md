# Frontend

## Table of contents
1. [Purpose](#purpose)
2. [Design Goals](#design-goals)
3. [Technology](#technology)
4. [General Philosophy](#general-philosophy)
5. [UI Architecture](#ui-architecture)
6. [Screen Layout](#screen-layout)
7. [Controls](#permanent-controls)
8. [REST API](#rest-api)
9. [POST Endpoints](#post-endpoints)
10. [Refresh Strategy](#refresh-strategy)
11. [Future WebSocket API](#future-websocket-api)
12. [Frontend Directory Structure](#frontend-directory-structure)
13. [JavaScript Responsibilities](#javascript-responsibilities)
14. [Current PWA and HTTPS Implementation](#current-pwa-and-https-implementation)
15. [Current Control Integration](#current-control-integration)
16. [Compact Smartphone Controls](#compact-smartphone-controls)
17. [Error Handling](#error-handling)
18. [Design Rules](#design-rules)

## Purpose

The Spy Turtle frontend is a mobile-first web application allowing the user to remotely control the robot.

The frontend contains **no robot intelligence**.

Its only responsibilities are:

* displaying robot information
* displaying the live camera stream
* sending user commands
* receiving robot status updates

All robot behaviour remains inside the Brain.

---

# Design Goals

The frontend follows a few simple principles.

* Mobile first
* Smartphone optimized
* Thumb friendly
* Fast loading
* Minimalistic
* Responsive
* Runs directly inside a browser
* Installable as a Progressive Web App
* Full-screen standalone launch on supported smartphones

The interface is designed primarily for smartphone usage but remains usable on tablets and desktop browsers for development and testing.

---

# Technology

Version 1 uses:

* HTML
* CSS
* Vanilla JavaScript

No frontend framework is required.

The frontend communicates with the robot using:

* REST API
* WebSocket (future)

The mobile application is a Progressive Web App (PWA) served directly by the Raspberry Pi.

Version 1 is already packaged as an installable PWA. The existing responsive HTML, CSS and Vanilla JavaScript codebase is reused directly, with a web manifest and service worker providing standalone launch and offline application assets.
---

# General Philosophy

The frontend is a **remote controller**, not the robot itself.

Its role is to expose robot capabilities in the simplest possible way.

Robot intelligence always remains inside the Brain.

The interface should never make autonomous decisions.

The frontend only:

* displays information
* sends user commands
* receives robot feedback

---

# UI Architecture

The interface is built around reusable visual components.

Main components:

* Control cards
* Direction controls
* Status widgets
* Camera view
* Selector controls
* Action buttons

The goal is to keep the interface modular and easy to evolve.

Future changes should be possible by modifying components rather than rewriting the whole interface.

---

# Screen Layout

The main screen uses a three-column layout.

Current proportions:

```
LEFT PANEL       CENTER PANEL        RIGHT PANEL

   18%              64%                 18%
```

Example:

```
+----------------------------------------------------------------+
|         | Battery WiFi Emotion LED Status |                    |
|         +---------------------------------+                    |
|         |                                 |                    |
| Control |                                 | Control            |
| Cards   |        Camera Stream            | Cards              |
|         |                                 |                    |
|         |                                 |                    |
+----------------------------------------------------------------+
```

The center panel contains:

* status bar
* live camera stream

The side panels contain:

Left:

* robot movement
* sound selector
* message panel

Right:

* camera/head movement
* face selector
* LED selector
* photo button

---

# Layout Principles

The interface follows these rules:

* The camera remains the main visual element.
* Side controls remain compact.
* Controls must remain reachable with both thumbs.
* Panels must never stretch vertically only to fill empty space.
* The camera aspect ratio must remain fixed.
* The interface must remain usable on small smartphone screens.

---

# Permanent Controls

These controls are always visible.

---

## Status Bar

The status bar is located above the camera.

It displays:

* battery percentage
* charging status
* WiFi status
* connection status
* current emotion
* current LED mode
* camera FPS (optional)

The status bar is intentionally compact and occupies only a small part of the screen height.

Example:

```
🔋92%   📶   🙂 Happy   🌈 Rainbow
```

A small turtle avatar may also display the current facial expression.

Examples:

```
(^_^)

(-_-)

(O_O)
```

---

# Camera

Displays the live stream from the Raspberry Pi Camera Module 3.

The camera:

* occupies approximately 60–70% of the available width
* keeps a fixed aspect ratio
* remains the main focus of the interface

Future additions:

* snapshot overlay
* video recording
* computer vision overlays

---

# Movement Controls

Controlled by the left thumb.

The movement control is displayed as a dedicated control card.

Buttons:

* Forward
* Backward
* Left
* Right
* STOP

The control will evolve toward a reusable D-Pad component.

Future design:

```
       ▲

    ◀  ●  ▶

       ▼
```

Holding a button continuously sends movement commands.

STOP immediately stops both motors.

---

# Head Controls

Controlled by the right thumb.

Buttons:

* Up
* Down
* Left
* Right
* Center

The head control uses the same design principles as the movement control.

Future version:

* Virtual joystick

---

# Secondary Controls

These controls are used less frequently but remain accessible.

---

# Face Selector

The face selector temporarily overrides the autonomous face behaviour.

Available expressions:

* Neutral
* Happy
* Curious
* Angry
* Sad
* Sleepy
* Surprised

The selected face remains active for approximately one minute before the Brain returns to autonomous expressions.

The selector is displayed as a compact control row:

```
🐢 [ Happy ▼ ]
```

---

# LED Selector

Available modes:

* Off
* Rainbow
* Breathing
* Pulse
* Ocean
* Fire
* Police
* Static White
* Static Red
* Static Green
* Static Blue

The selector is displayed as a compact control row:

```
💡 [ Rainbow ▼ ]
```

---

# Sound Selector

Predefined sounds.

Examples:

* Startup
* Beep
* Happy
* Angry
* Sleep
* Curious

The selector is displayed as a compact control row:

```
🔊 [ Startup ▼ ]
```

Future:

* Text-to-speech

---

# Message Panel

Simple text box.

Example:

```
Hello!
```

The message is displayed on the shell TFT screen. Temporary shell content returns to Status after a configurable timeout. Message submission can be triggered with **Enter**, avoiding an unnecessary Send button on compact smartphone layouts.

---

# Picture Button

Captures a still image from the camera.

The button uses a standard camera-style design:

```
  ◯
  🔴
```

The picture is stored on the Raspberry Pi and may later be downloaded.

---

# REST API

Version 1 uses REST.

Future versions may progressively migrate toward WebSockets.

---

# GET Endpoints

## GET /status

Returns:

```json
{
    "battery":92,
    "charging":false,
    "emotion":"happy",
    "led_mode":"rainbow",
    "connection":"online",
    "wifi":true
}
```

---

## GET /camera

Returns the MJPEG live stream.

---

## GET /faces

Returns available expressions.

Example:

```json
[
    "neutral",
    "happy",
    "curious",
    "sad",
    "sleepy",
    "angry",
    "surprised"
]
```

---

## GET /led_modes

Returns all available LED modes.

---

## GET /sounds

Returns all available predefined sounds.

---

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