# REST API

The API allows remote control.

## Movement

```
POST /move/forward
POST /move/backward
POST /move/left
POST /move/right
POST /move/stop
```

---

## Camera

```
POST /camera/start
POST /camera/stop

POST /camera/left
POST /camera/right
POST /camera/up
POST /camera/down
POST /camera/center

GET /camera/frame
```

---

## LEDs

```
POST /led/{mode}
```

---

## Face

```
POST /emotion/{emotion}
```

---

## Speaker

```
POST /speak/{text}
```

---

## Battery

```
GET /battery
```

Example:

```json
{
    "level":100,
    "charging":false
}
```

---

# Startup

The official startup command is:

```
python -m robot.startup.main
```

Startup sequence:

```
Create Robot
      |
Register Runtime
      |
Start API
      |
Start Robot Loop
```

---

# Coding Rules

The project follows these rules:

* Keep code compact and readable.
* Avoid unnecessary blank lines.
* Prefer inline expressions when they remain readable.
* Avoid splitting simple logic into many artificial blocks.
* Always provide complete files when modifying project files.
* Keep simulation and hardware APIs identical.
* Never put hardware-specific code inside Brain or API logic.

---

# Development Workflow

Development:

```
RobotFactory(simulation=True)
```

Runs on:

* Windows
* VS Code
* Python virtual environment

Production:

```
RobotFactory(simulation=False)
```

Runs on:

* Raspberry Pi 5
* real hardware components

---

# Assets
All reusable media is stored under `robot/assets/` and indexed through `assets.json`.

```text
robot/assets/
├── assets.json
├── assets.py
├── eyes/
├── fonts/
├── images/
└── sounds/
```

`AssetCatalog` resolves named assets and exposes defaults, lists, availability checks and reload support. Hardware/UI modules consume asset names rather than hard-coded paths.

---

# Eye Animation System
Eye expressions are animation sequences defined in a shared `sequences.json`. Sequence groups include frontend-selectable emotions, autonomous idle sequences, Brain-triggered sequences and transient actions such as blink, double blink, directional looks, yawn and wake-up. Idle operation distinguishes at least ACTIVE and SLEEP modes.

---

# Shell Display System
The ST7796U shell screen supports Status, Log, Message, Image, GIF and Countdown-style modes. Temporary media modes use a configurable timeout and return to Status. The shell controller stores the active mode and mode-specific state while views perform rendering. Status is intended to mirror the most useful frontend telemetry.

---

# LED Hardware on Raspberry Pi 5
WS2812B output uses the official PIO overlay:

```ini
dtoverlay=ws2812-pio,gpio=18,num_leds=32,brightness=255
```

The hardware backend opens `/dev/leds0`, enables brightness pass-through with a zero byte, writes RGB pixel bytes and closes the descriptor. It does not use `rpi_ws281x` and does not seek within the character device.

---

# Servo Runtime
Each servo has configurable center, minimum, maximum, movement range and speed. Frontend commands change the target angle. `Robot.update()` gradually moves the current angle toward the target and detaches PWM after the target is reached to reduce jitter and power use.

---

# Logging and Startup
`scripts/start_turtle.sh` is the common manual and systemd startup entry point. Logs rotate by startup:

```text
logs/turtle.log.1
logs/turtle.log.2
logs/turtle.log.3
logs/log -> turtle.log.1
```

Python runs unbuffered so crash-adjacent output is written promptly. `spyturtle.service` starts the application automatically, while Caddy provides local HTTPS for the PWA.

---

# Current Status
Completed or operational:
- Shared Robot/Brain architecture with simulation and hardware factories.
- REST API and mobile frontend control.
- Camera Module 3 integration.
- UPS battery access.
- ST7796U shell display and shell view/controller architecture.
- Asset catalog for eyes, images, GIFs, fonts and sounds.
- Eye animation sequences for frontend, idle, Brain and transient actions.
- Smooth target-based servo movement with automatic detachment.
- Raspberry Pi 5 WS2812 output through `/dev/leds0`.
- PWA packaging, local HTTPS through Caddy and automatic startup through systemd.
- Startup log rotation and stable `logs/log` symbolic link.

Pending:
- Motor and encoder hardware integration.
- Final dual OLED eye integration.
- Final audio hardware path.
- Additional coordinated behaviors across shell, eyes and LEDs.
