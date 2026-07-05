# Spy Turtle - Wiring Guide

## Overview

This document describes the planned electrical connections for Spy Turtle Version 1.

The goal is to keep wiring simple, modular and easy to maintain.

---

# Main Components

* Raspberry Pi 5
* Waveshare UPS HAT (4-cell version)
* Raspberry Pi Camera Module 3
* TB6612FNG Motor Driver
* Two JGA25-370 DC Motors with Encoders
* Two SSD1306 OLED Displays
* WS2812B LED Strip
* MAX98357A I²S Amplifier + Speaker
* MG90S Servos
* GPIO Breakout Board

---

# Power Architecture

```
18650 Batteries
        │
        ▼
Waveshare UPS HAT
        │
        ▼
 Raspberry Pi 5
        │
        ├── GPIO
        ├── USB
        ├── Camera
        └── I²C
```

During software development, the Raspberry Pi can also be powered directly through the USB-C connector.

---

# Camera

Interface:

* CSI ribbon cable

Connection:

```
Camera Module
        │
        ▼
CSI Connector
```

No GPIO pins are required.

---

# Motor Driver

The TB6612FNG controls both drive motors.

Connections:

* Motor A
* Motor B
* VM (motor power)
* VCC
* GND
* PWM pins
* Direction pins
* STBY

Encoder outputs connect directly to Raspberry Pi GPIO pins.

---

# OLED Displays

Two identical SSD1306 displays share the same I²C bus.

Display 1

* Face / Eyes

Display 2

* Messages / Status (future)

Connections:

* SDA
* SCL
* 3.3V
* GND

One display address may need to be changed depending on the module version.

---

# WS2812 LED Strip

Purpose:

* Shell lighting
* Status indication
* Animations

Connections:

* 5V
* GND
* Data

Initial testing will be performed directly from the Raspberry Pi GPIO.

A logic level shifter may be added later if required.

---

# Audio

The MAX98357A amplifier uses I²S.

Connections:

* BCLK
* LRCLK
* DIN
* 5V
* GND

The speaker connects directly to the amplifier module.

---

# Servo Motors

Planned uses:

* Head movement
* Future accessories

Connections:

* PWM
* 5V
* GND

---

# GPIO Breakout Board

The breakout board serves as the central wiring hub.

Advantages:

* easier maintenance
* cleaner wiring
* easier troubleshooting
* simpler upgrades

Most modules should connect to the breakout board rather than directly to the Raspberry Pi.

---

# Cable Management

Recommended practices:

* Keep motor wires away from camera cables.
* Secure cables with zip ties.
* Leave enough slack for moving parts.
* Label critical connectors whenever possible.

---

# Cooling

The Raspberry Pi 5 uses an active cooler.

Ensure adequate airflow inside the shell.

Do not obstruct the fan.

---

# External Connectors

The chassis exposes:

* USB-C charging port (panel mount extension)

Future versions may also expose:

* Power switch
* Maintenance USB port
* Debug connector

---

# Assembly Strategy

Recommended installation order:

1. Raspberry Pi
2. UPS HAT
3. Active Cooler
4. Camera
5. Breakout Board
6. OLED Displays
7. Motor Driver
8. Motors
9. Speaker
10. LED Strip
11. Servos
12. Cable Management

Test each subsystem before installing the next one.

This approach makes troubleshooting significantly easier.
