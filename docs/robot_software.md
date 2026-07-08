# Spy Turtle - Robot Software Architecture

## Purpose

The `robot` package contains all software running on the Spy Turtle robot itself.

It includes:

* robot intelligence
* behaviour management
* hardware abstraction
* simulation
* communication services
* system state management

The robot software is independent from the mobile frontend.

The frontend only sends commands and displays information.

---

# Architecture Overview

Spy Turtle follows a layered architecture:

```
Mobile Frontend
        |
        | REST API / WebSocket
        |
       API
        |
      Brain
        |
   System Layer
        |
 Hardware Interfaces
        |
 Simulation / Real Hardware
```

The robot software must run identically in simulation and on the physical Raspberry Pi.

---

# Design Principles

## Simulation First

Every hardware component must provide a simulation implementation.

The same Brain must work with:

* simulated hardware
* real hardware

The Brain must never know whether it controls a real motor or a simulated motor.

Example:

Good:

```python
motor.move_forward()
```

The Brain only requests an action.

Bad:

```python
GPIO.output(pin, HIGH)
```

Hardware details must remain isolated.

---

# Separation of Responsibilities

## Brain

Location:

```
robot/brain/
```

The Brain contains all robot intelligence.

Responsibilities:

* autonomous behaviours
* emotional decisions
* reactions to user interaction
* idle behaviours
* decision making

Examples:

* deciding when to blink
* deciding when to look around
* selecting an expression
* reacting to commands

The Brain does not directly control hardware.

---

## System

Location:

```
robot/system/
```

The System layer represents the robot itself.

Responsibilities:

* robot assembly
* global state
* coordination between modules

Contains:

```
robot.py
state.py
```

The Robot object creates and connects all required components.

Example:

```
Robot
 |
 +-- Brain
 |
 +-- Face
 |
 +-- Motors
 |
 +-- Camera
 |
 +-- LEDs
 |
 +-- Battery
```

---

## Hardware

Location:

```
robot/hardware/
```

Hardware modules provide abstract interfaces to physical components.

Examples:

```
motor.py
camera.py
oled.py
leds.py
speaker.py
battery.py
servo.py
```

Hardware modules:

* know how to communicate with devices
* do not contain behaviour
* do not make decisions

---

## Face System

Location:

```
robot/face/
```

The face system manages Spy Turtle's expressions.

Responsibilities:

* eyes
* mouth
* animations
* expressions

The face system receives commands but does not decide when emotions happen.

Example:

The Brain decides:

```
show happy expression
```

The Face system handles:

```
how happy is displayed
```

---

## API

Location:

```
robot/api/
```

The API provides communication with external clients.

Responsibilities:

* receiving user commands
* sending robot status
* exposing camera stream

The API does not contain robot intelligence.

---

## Simulation

Location:

```
robot/simulation/
```

The simulation environment allows development without physical hardware.

Simulation components replace real hardware:

```
Real Motor       Fake Motor
Real OLED   ->   Fake OLED
Real LEDs        Fake LEDs
```

The goal is to develop most software before the Raspberry Pi assembly.

---

# Startup

Location:

```
robot/startup/
```

The startup module launches the robot software.

Responsibilities:

* initialize the robot
* start required services
* run the main execution loop

---

# Configuration

Location:

```
robot/config/
```

Contains configuration values:

* hardware settings
* robot parameters
* timing values
* environment configuration

---

# Development Rules

When adding a new feature:

1. Add behaviour to the Brain.
2. Add hardware access through an interface.
3. Add a simulation implementation.
4. Test without physical hardware.
5. Deploy to Raspberry Pi only after simulation works.

---

# Current Architecture

```
robot/

├── api/
├── brain/
├── config/
├── face/
├── hardware/
├── simulation/
├── startup/
├── system/
└── tests/
```

---

# Future Extensions

The architecture should allow adding:

* computer vision
* autonomous navigation
* speech recognition
* speech synthesis
* object recognition
* emotional memory
* advanced AI behaviours

without redesigning the core system.

---

# Project Philosophy

Spy Turtle is not designed to be only a remote-controlled robot.

The software architecture exists to create the feeling of a small living creature.

The Brain provides personality.

The hardware provides senses and movement.

The simulation provides freedom to experiment.

Every technical decision should help Spy Turtle feel alive.
