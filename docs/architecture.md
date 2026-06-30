🐢 Spy Turtle — System Architecture
# 🐢 Spy Turtle — System Architecture

## 🎯 Project Goal

Spy Turtle is a Raspberry Pi 5-based mobile robot designed for:

- Remote control from a smartphone or browser
- Live video streaming
- Audio interaction (speech in/out)
- LED lighting effects
- Extendable AI / vision capabilities

The project is designed as a **modular robotics platform for learning and experimentation**.

---

## 🧱 High-Level Architecture


[ Smartphone / Browser UI ]
↓ WiFi
[ Web API ]
↓
[ Robot Controller ]
↓
┌──────────────────────────┐
│ Hardware Layer │
│--------------------------│
│ Motor Driver (TB6612) │
│ Camera (CSI) │
│ LEDs (WS2812) │
│ Audio (I2S amplifier) │
│ OLED Display (I2C) │
│ Fan (GPIO / MOSFET) │
└──────────────────────────┘
↓
Raspberry Pi 5
↓
Waveshare UPS HAT 2S
↓
2x18650 Battery Pack


---

## 🧠 Software Architecture

### Entry Point


software/app/main.py


Responsible for starting the robot system.

---

### Robot Core API


software/app/robot.py


Provides a simple high-level interface:

```python
robot.forward()
robot.backward()
robot.turn_left()
robot.turn_right()
robot.stop()

This is the ONLY interface used by higher layers.

Hardware Abstraction Layer
software/hardware/

Responsibilities:

GPIO control
Motor driver (TB6612)
LED control
Display control
Fan control
Audio interface

👉 This layer MUST NOT contain web or UI logic.

API Layer (future)
software/api/

Planned REST + WebSocket interface:

POST /api/motor
POST /api/photo
POST /api/led
POST /api/speak
POST /api/display
Web Interface
software/web/

Features:

Mobile-friendly dashboard
Live camera stream
Joystick control
Action buttons (LED, audio, fan, photo)
🧪 Simulation Mode

The system supports a simulation mode for development without hardware:

SIMULATION = True

Allows full software testing on a PC.

🔋 Power System
Waveshare UPS HAT 2S (5V output)
2×18650 Li-ion battery pack (2S configuration)
Provides stable power for Raspberry Pi 5 and peripherals
🔌 GPIO Strategy
TB6612 motor driver for dual DC motors
PWM control for speed
Digital GPIO for direction
Encoder inputs reserved for future odometry
🧭 Development Philosophy
Strict separation of layers
Hardware isolated from application logic
Simulation-first development
Modular and testable components
API-driven design for future expansion

🚀 Roadmap
v0.1 — Foundation
Project structure
Simulation motor system
v0.2 — Mobility
Real motor control (TB6612)
Basic movement
v0.3 — Vision
Camera integration
Live streaming
v0.4 — Remote Control
Web dashboard
Mobile UI
v0.5 — Interaction
LEDs
Audio system
Display + fan
v1.0 — Full Robot
Stable mobile robot
Fully remote controlled Spy Turtle