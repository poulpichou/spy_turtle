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

Spy Turtle follows this architecture:

    Mobile Frontend
            |
            | REST API / WebSocket
            |
           API
            |
          Robot
            |
          Brain
            |
       System Layer
            |
     Hardware Interfaces
            |
     Simulation / Real Hardware

The robot software must run identically in simulation and on the physical Raspberry Pi.

---

# Design Principles

## Simulation First

Every hardware component must provide a simulation implementation.

The same Brain must work with:

* simulated hardware
* real hardware

The Brain must never know if it controls real or simulated components.

Example:

Good:

    motor.move_forward()

Bad:

    GPIO.output(pin, HIGH)

Hardware details remain isolated.

---

## Modular Behaviour

The Brain coordinates independent behaviour modules.

Current structure:

    robot/brain/

    brain.py
    idle.py
    commands.py
    emotions.py
    planner.py

Responsibilities:

### IdleBehaviour

Handles autonomous behaviours:

* blinking
* looking around
* yawning
* small idle actions

### CommandManager

Handles user interaction:

* movement commands
* user priorities
* temporary interaction state

### EmotionManager

Handles emotional state:

* current emotion
* expression requests

### Planner

Decides which behaviour currently has priority.

---

# Behaviour Priority

Behaviours must not compete directly.

The Planner decides which behaviour is allowed to run.

Current priority model:

    100 : emergency / safety
    50  : user interaction
    30  : emotions
    10  : idle behaviour

Examples:

* user commands temporarily override idle behaviour
* low battery can override normal behaviour
* emergency stop overrides everything

---

# Separation of Responsibilities

## Robot

Location:

    robot/system/

The Robot object represents the complete robot.

Responsibilities:

* connect all modules
* contain global state
* expose high-level actions
* run Brain updates

Contains:

    robot.py
    state.py

Example:

    Robot
     |
     +-- State
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

---

## Brain

Location:

    robot/brain/

The Brain contains robot intelligence.

Responsibilities:

* autonomous behaviours
* emotional decisions
* reactions to user interaction
* behaviour scheduling
* decision making

Examples:

* deciding when to blink
* deciding when to look around
* selecting expressions
* reacting to commands

The Brain never directly accesses hardware.

---

## Hardware

Location:

    robot/hardware/

Hardware modules provide interfaces to physical components.

Examples:

    motor.py
    camera.py
    oled.py
    leds.py
    speaker.py
    battery.py
    servo.py

Hardware modules:

* communicate with devices
* hide implementation details
* do not contain behaviour
* do not make decisions

---

## Face System

Location:

    robot/face/

The Face system manages Spy Turtle expressions.

Responsibilities:

* eyes
* mouth
* animations
* expressions

The Face receives commands but does not decide when emotions happen.

Example:

Brain decides:

    show happy expression

Face handles:

    display happy expression

---

## API

Location:

    robot/api/

The API communicates with external clients.

Responsibilities:

* receiving user commands
* sending robot status
* exposing services such as camera streaming

The API does not contain robot intelligence.

Correct flow:

    API
     |
     v
    Robot
     |
     v
    Brain
     |
     v
    Hardware

---

# Robot Factory

Location:

    robot/factory/

The Factory creates complete robot instances.

Responsibilities:

* select simulation or hardware components
* hide initialization details
* allow the same software to run everywhere

Example:

    robot = RobotFactory.create(simulation=True)

Simulation components:

    FakeMotor
    FakeFace
    FakeOLED

Hardware components:

    MotorDriver
    OLED
    Camera
    LEDs

The rest of the software must not know which implementation is used.

---

# Simulation

Location:

    robot/simulation/

The simulation environment allows development without physical hardware.

Simulation replaces real components:

    Real Motor   -> Fake Motor
    Real OLED    -> Fake OLED
    Real LEDs    -> Fake LEDs
    Real Camera  -> Fake Camera

The goal is to develop most software before Raspberry Pi assembly.

---

# Startup

Location:

    robot/startup/

The startup module launches the robot software.

Responsibilities:

* create robot using RobotFactory
* initialize services
* run the main loop

Startup must not contain robot behaviour.

---

# Configuration

Location:

    robot/config/

Contains:

* hardware settings
* robot parameters
* timing values
* environment configuration

---

# Development Rules

When adding a new feature:

1. Add behaviour logic to the Brain.
2. Add hardware access through an interface.
3. Add simulation implementation.
4. Test without physical hardware.
5. Deploy to Raspberry Pi only after simulation works.

---

# Code Style Rules

The project prefers simple and compact code.

Rules:

* avoid unnecessary blank lines
* avoid unnecessary line breaks
* keep related instructions close together
* prefer readable compact functions
* avoid over-engineering
* avoid excessive abstraction

The objective is readability and maintainability.

Preferred style:

    self.robot.forward()
    self.robot.set_emotion("happy")

Avoid unnecessary splitting:

    self.robot \
        .forward()

    self.robot \
        .set_emotion(
            "happy"
        )

---

# Current Architecture

    robot/

    ├── api/
    ├── brain/
    ├── config/
    ├── factory/
    ├── face/
    ├── hardware/
    ├── simulation/
    ├── startup/
    ├── system/
    └── tests/

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