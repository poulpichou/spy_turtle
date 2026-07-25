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

