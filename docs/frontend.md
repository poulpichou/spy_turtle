# Frontend

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
* Portrait orientation
* Thumb friendly
* Fast loading
* Minimalistic
* Responsive
* No installation required
* Runs directly inside a browser

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

---

# General Philosophy

The frontend is a **remote controller**, not the robot itself.

Its role is to expose robot capabilities in the simplest possible way.

Robot intelligence always remains inside the Brain.

The interface should never make autonomous decisions.

---

# Screen Layout

```
+--------------------------------------------------------------------------------+
| Battery | WiFi | Connection | FPS | Emotion | LED Mode | Robot Avatar | Status |
+--------------------------------------------------------------------------------+
|            |                                             |                     |
| Movement   |                                             | Head                |
| Controls   |                                             | Controls            |
|            |                                             |                     |
|            |                                             |                     |
| Sound      |            Live Camera Stream               | Face                |
| Selector   |                                             | Selector            |
|            |                                             |                     |
| Message    |                                             | LED                 |
| __________ |                                             | Selector            |
| |        | |                                             |                     |
| |________| |                                             |                     |
|  [Send]    |                                             | [Take Picture]      |
+--------------------------------------------------------------------------------+
```

The live camera should occupy approximately **60–70%** of the available screen.

The movement and head controls remain permanently visible.

Secondary controls remain easily reachable without hiding the camera.

All controls should remain usable with both thumbs.

---

# Permanent Controls

These controls are always visible.

## Status Bar

Displays:

* battery percentage
* charging status
* WiFi status
* connection status
* current emotion
* current LED mode
* camera FPS (optional)

A small avatar of the turtle may also display the current facial expression.

Examples:

```
(^_^)
(-_-)
(O_O)
```

---

## Camera

Displays the live stream from the Raspberry Pi Camera Module 3.

Future additions:

* snapshot overlay
* video recording
* computer vision overlays

---

## Movement Controls

Controlled by the left thumb.

Buttons:

* Forward
* Backward
* Left
* Right
* STOP

Holding a button continuously sends movement commands.

STOP immediately stops both motors.

---

## Head Controls

Controlled by the right thumb.

Buttons:

* Up
* Down
* Left
* Right
* Center

Future version:

* Virtual joystick

---

# Secondary Controls

These controls are used less frequently but remain accessible.

---

## Face Selector

Temporarily overrides the autonomous face.

Examples:

* Neutral
* Happy
* Curious
* Angry
* Sad
* Sleepy
* Surprised

The selected face remains active for approximately one minute before the Brain returns to autonomous expressions.

---

## LED Selector

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

---

## Sound Selector

Predefined sounds.

Examples:

* Startup
* Beep
* Happy
* Angry
* Sleep
* Curious

Future:

* Text-to-speech

---

## Message Panel

Simple text box.

Example:

```
Hello!
```

The message is displayed on the OLED face.

The Brain decides how long it remains visible.

---

## Picture Button

Captures a still image from the camera.

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
    "battery": 92,
    "charging": false,
    "emotion": "happy",
    "led_mode": "rainbow",
    "connection": "online",
    "wifi": true
}
```

---

## GET /camera

Returns the MJPEG live stream.

---

## GET /faces

Returns the available expressions.

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
