# Spy Turtle - Software Architecture

## Overview

Spy Turtle is designed as a modular robotics platform rather than a collection of scripts. Every subsystem has a single responsibility, making the project easy to maintain, extend and debug.

The robot is organized into four main layers:

```
                +------------------+
                |      Robot       |
                +------------------+
                         |
      +------------------+------------------+
      |                  |                  |
      v                  v                  v
 +------------+   +---------------+   +-------------+
 |  Hardware  |   |  Personality  |   |    Brain    |
 +------------+   +---------------+   +-------------+
      \               /                    /
       \             /                    /
        +-----------+--------------------+
                    |
                    v
             State Machine
```

The `Robot` object acts as the central coordinator. It owns every subsystem and provides a single API for the application.

---

# Project Structure

```
software/

├── app/
│   ├── main.py
│   └── robot.py
│
├── hardware/
│   ├── battery.py
│   ├── camera.py
│   ├── leds.py
│   ├── motors.py
│   ├── oled.py
│   ├── servo.py
│   └── speaker.py
│
├── personality/
│   ├── emotion_engine.py
│   ├── emotions.py
│   ├── moods.py
│   └── events.py
│
├── brain/
│   ├── planner.py
│   └── state_machine.py
│
├── api/
│
└── config/
    └── settings.py
```

---

# Robot

The `Robot` class owns every subsystem.

Example:

```python
robot.camera
robot.motors
robot.display
robot.audio
robot.emotions
robot.brain
```

The rest of the application should interact with the robot through these high-level interfaces.

---

# Hardware Layer

The hardware layer contains all Raspberry Pi specific code.

Responsibilities include:

* GPIO
* PWM
* I²C
* SPI
* Camera
* Audio
* Motors
* Battery monitoring

The hardware layer **must never contain application logic**.

Its only responsibility is controlling physical devices.

---

# Personality Layer

The personality layer gives Spy Turtle its character.

It manages:

* emotions
* moods
* reactions
* future animations
* future voice personality

Examples of emotions:

* Happy
* Curious
* Thinking
* Sleepy
* Loving
* Angry
* Error

The personality layer does not know how LEDs or displays work.

It only describes the robot's internal emotional state.

---

# Brain Layer

The brain is responsible for decision making.

Future responsibilities include:

* navigation
* planning
* target selection
* exploration
* interaction
* AI integration

The brain decides **what** the robot should do.

It does not control hardware directly.

---

# State Machine

Spy Turtle always operates in one high-level state.

Initial planned states:

```
BOOT

↓

IDLE

↓

EXPLORE

↓

INTERACT

↓

FOLLOW

↓

SLEEP

↓

CHARGE

↓

ERROR
```

Each state defines:

* allowed behaviours
* active sensors
* movement policy
* default emotion

---

# Events

The robot communicates internally using events.

Examples:

```
BOOT

PERSON_DETECTED

PERSON_LOST

BATTERY_LOW

BATTERY_OK

OBSTACLE_DETECTED

VOICE_COMMAND

TOUCH

ERROR
```

Hardware generates events.

The brain consumes events.

The personality reacts to them.

---

# Design Principles

Spy Turtle follows several simple rules.

## Separation of responsibilities

Each module has one job.

## Hardware independence

Application logic should not depend on GPIO details.

## Extensibility

Adding a new sensor or actuator should require minimal changes.

## Readability

The code should remain understandable for children and hobbyists.

## Testability

Whenever possible, hardware modules should be replaceable with simulated versions during development.

---

# Long-Term Vision

Spy Turtle is intended to become a reusable robotics framework.

Future robots (fox, dinosaur, bear, etc.) should be able to reuse most of the software by replacing only:

* the 3D printed body
* animations
* behaviours
* hardware configuration

The architecture is designed to support this long-term goal.
