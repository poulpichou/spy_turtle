# Spy Turtle

## Overview

Spy Turtle is a small robotic turtle built around a Raspberry Pi 5.

It combines robotics, embedded electronics, computer vision and expressive animations into a compact platform that feels less like a machine and more like a small living creature.

The robot can be remotely controlled from a smartphone while also exhibiting autonomous behaviours such as blinking, looking around, yawning and expressing emotions.

The project is designed to be fun to build, easy to understand and highly modular.

---

# Current Version (V1)

Version 1 focuses on building a reliable, expressive and remotely controlled robot.

The objective is not to build an autonomous AI companion immediately, but to validate the complete hardware and software architecture.

Version 1 includes:

* remote driving
* live camera streaming
* animated OLED face
* RGB shell LEDs
* sound playback
* battery monitoring
* smartphone web interface
* complete software simulation

Everything else is considered a future extension.

---

# Project Goals

Spy Turtle follows a few simple principles.

## Personality First

Spy Turtle is not simply a remote-controlled robot.

Its primary goal is to appear alive.

Even when idle, it should:

* blink naturally
* look around
* yawn
* become sleepy
* express emotions
* react to user interaction

The robot should never feel "frozen".

---

## Modular Design

Every hardware component is isolated behind a software interface.

Replacing a display, a motor driver or the camera should require little or no modification to the rest of the codebase.

---

## Simulation First

Every hardware module must have a software simulation.

The exact same Brain module should run on:

* the simulator
* the Raspberry Pi

without modification.

This allows almost all software development to happen before the robot is assembled.

---

## Mobile First

Spy Turtle is primarily controlled from a smartphone.

Desktop browsers are used only for development.

The user interface is designed around portrait orientation and two-handed operation.

---

## Simplicity

Whenever several solutions exist, the simplest reliable solution is preferred.

Readability and maintainability are considered more important than technical sophistication.

Preference for not having to solder anything whenever reasonably possible.

---

# Behaviour Philosophy

Spy Turtle should never appear perfectly deterministic.

Small random behaviours make the robot feel alive.

Examples include:

* blinking at irregular intervals
* occasionally looking around
* tiny eye movements
* yawning after being idle
* slowly changing emotional state
* reacting to user interactions

These behaviours should remain subtle enough that they never interfere with user commands.

---

# Design Constraints

The project intentionally follows a few engineering constraints.

* Everything must run locally on the Raspberry Pi.
* Internet access must not be required.
* The robot must boot automatically after power-on.
* The simulator and the real robot must share the exact same Brain.
* Every hardware component should be replaceable independently.
* Behaviour must never depend directly on hardware implementations.

---

# Hardware Platform

## Main Computer

* Raspberry Pi 5
* 64 GB A2 microSD

## Power System

* Waveshare UPS HAT (4-cell version)
* 4 × Samsung 21700 Li-Ion cells
* External USB-C panel mount charging connector

## Mobility

* 2 × JGA25-370 DC motors (6 V, 280 RPM)
* Wheel encoders
* TB6612FNG motor driver
* 2WD chassis

## Vision

* Raspberry Pi Camera Module 3

## User Feedback

* 2 × 0.96" OLED displays
* WS2812 addressable RGB LEDs
* MAX98357A I2S amplifier
* Speaker

## Motion

* 2 × MG90S servos

## Microphone

* (Version 2) Not purchased yet

---

# Software Architecture

The software is organised into independent layers.

```
Mobile Frontend
        │
 REST API / WebSocket
        │
    Robot Brain
        │
 Hardware Interfaces
        │
Simulation / Real Hardware
```

The Brain contains all robot behaviour.

The frontend only displays information and sends commands.

Hardware modules never contain behavioural logic.

---

# Planned Features

## Remote Driving

* Forward
* Backward
* Turn left
* Turn right

---

## Expressive Face

Available expressions:

* Neutral
* Happy
* Curious
* Sleepy
* Sad
* Angry
* Surprised
* Scared

Available animations:

* Blink
* Double blink
* Wink
* Yawn
* Look left
* Look right
* Idle eye movement

Animations are automatically triggered while the robot is idle (typically every few seconds).

When the user manually selects an expression, it remains active for approximately one minute before returning to autonomous behaviour.

---

## Camera

* Live video stream
* Mobile preview
* Future computer vision capabilities

---

## LED Animations

Examples include:

* Rainbow
* Breathing
* Pulse
* Ocean
* Fire
* Police
* Static colours
* Off

---

## Audio

The robot can:

* play sounds
* acknowledge commands
* express emotions
* provide simple feedback

Version 2 ideas:

* relay the user's voice
* speak custom text

---

## Battery Management

The software monitors:

* battery percentage
* charging state
* UPS status
* estimated remaining runtime

---

# Mobile Application

The smartphone application provides:

* live camera stream
* driving controls
* expression selector
* LED controls
* battery status
* current emotion
* current LED mode
* robot status

The camera occupies approximately 60–70% of the screen while controls remain easily reachable with both thumbs.

## Frontend Specifications

The interface shall provide:

* control to move forward, backward, turn left and turn right
* control to move the head (camera) left, right, up and down
* control to temporarily change the face shown on the OLED display (approximately one minute)
* control to select LED animations (blinking, rainbow, rotating, breathing, etc.)
* control to take a picture
* control to send a message to the shell display
* control to trigger predefined sounds

Version 2 ideas:

* relay the user's voice to the robot
* send text for speech synthesis
* relay microphone audio back to the user

High-level layout:

* movement controls on the lower left (~15% width)
* head controls on the lower right (~15% width)
* live camera stream occupying the center of the screen
* status bar at the top displaying battery level, connection status and robot state
* additional buttons, drop-down lists and text fields in the remaining available space

The interface must remain fully usable on a smartphone held in portrait orientation.

---

# Development Philosophy

The project follows several engineering rules.

* Prefer simple solutions.
* Keep modules independent.
* Separate hardware from behaviour.
* Separate behaviour from presentation.
* Write readable code.
* Test everything in simulation first.
* Keep documentation up to date.
* Avoid unnecessary dependencies.

Whenever possible:

**Simulation first.**

Every feature should work inside the simulator before being deployed to the Raspberry Pi.

---

# Current Status

The complete Version 1 hardware platform has been selected and ordered.

Development currently focuses on:

* software architecture
* simulator
* robot behaviour
* frontend
* REST API

Once the Raspberry Pi arrives, simulated hardware modules will progressively be replaced by their physical implementations without changing the Brain logic.

---

# Future Extensions

Potential future capabilities include:

* autonomous exploration
* computer vision
* speech recognition
* speech synthesis
* microphone streaming
* object recognition
* people tracking
* autonomous charging
* advanced emotional behaviours
* AI-assisted interactions

These features should integrate naturally into the existing architecture without requiring a redesign of the software.

---

# Project Vision

Spy Turtle is intended to become a small autonomous companion robot.

The objective is not to build the smartest robot.

The objective is to build one that feels the most alive.

Every design decision should contribute to this illusion.