# Wiring

## Purpose
This document describes the complete hardware assembly of Spy Turtle.

It is the reference for:
- hardware architecture
- electrical wiring
- GPIO allocation
- power distribution
- mechanical integration
- hardware configuration

Any hardware modification must be reflected in this document.

---

# Hardware Overview

Spy Turtle is built around a Raspberry Pi 5.

The Raspberry Pi contains all software intelligence and communicates with all hardware subsystems.

Main systems:
- Computer System
- Power System
- Vision System
- Display System
- Mobility System
- Head Articulation System
- Audio System
- Lighting System

---

# Final Bill Of Materials

## Main Computer
| Component | Quantity |
|---|---:|
| Raspberry Pi 5 | 1 |
| 64GB microSD A2 | 1 |
| GeeekPi Active Cooler | 1 |

---

# Power System
| Component | Quantity |
|---|---:|
| Waveshare UPS HAT | 1 |
| 21700 Li-Ion batteries | 4 |
| USB-C Panel Mount | 1 |
| Inline Fuse Holder | 1 |
| 5A Fuse | 1 |

The UPS HAT provides:
- battery charging
- battery protection
- uninterrupted power
- battery monitoring

Power distribution:
Battery pack  
→ Waveshare UPS HAT  
→ Raspberry Pi 5  
→ Low power peripherals

Battery system  
→ Motor driver  
→ Motors

---

# Vision System

## Camera
Component: Raspberry Pi Camera Module 3
Connection:  CSI interface directly connected to Raspberry Pi 5
Power: Supplied by Raspberry Pi
Software: camera.py

# Display System
Spy Turtle uses three displays:
- Left OLED eye
- Right OLED eye
- Shell TFT display

## Eye Displays
Components:
- 0.96 inch OLED
- 128x64 resolution
- SSD1306 driver
- I2C interface

Both displays share the same I2C bus.

GPIO allocation:

| Signal | Raspberry Pi GPIO |
|---|---|
| SDA | GPIO 2 |
| SCL | GPIO 3 |

Typical addresses:

| Display | Address |
|---|---|
| Left Eye | 0x3C |
| Right Eye | 0x3D |

Software: eyes.py

Functions:
- facial expressions
- emotions
- animations
- status feedback

---
## Shell TFT Display
The turtle shell uses a larger color display.

Components:
- 3.5 inch IPS TFT
- 320x480 resolution
- ST7796U driver
- SPI interface

Touch controller:
- FT6336U
- I2C interface

Touch status:
- Hardware available
- Disabled in Version 1

Purpose:
- displaying messages
- animations
- robot status
- user feedback

---

## TFT SPI Connection

| Signal | Raspberry Pi GPIO |
|---|---|
| MOSI | GPIO 10 |
| MISO | GPIO 9 |
| SCLK | GPIO 11 |
| CS | GPIO 8 |

Additional signals:
| Signal | Status |
|---|---|
| DC | Validate during assembly |
| RESET | Validate during assembly |
| Backlight | 5V |

Software: shell_display.py

---

# Mobility System
The mobility system controls the two wheels.

Components:
- TB6612FNG motor driver
- 2 x JGA25-370 DC motors
- Hall encoders

The Raspberry Pi does not power the motors directly.

The TB6612FNG receives control signals from the Raspberry Pi and provides the required current to the motors.

---

## Motor Control
The TB6612FNG is a dual H-Bridge motor driver.

It controls:
- motor direction
- motor speed through PWM
- motor activation

GPIO allocation:

| Signal | Raspberry Pi GPIO |
|---|---|
| PWMA | GPIO 12 |
| AIN1 | GPIO 5 |
| AIN2 | GPIO 6 |
| PWMB | GPIO 13 |
| BIN1 | GPIO 16 |
| BIN2 | GPIO 20 |
| STBY | GPIO 4 optional |

---

## Encoder Feedback
The JGA25-370 motors include Hall effect encoders.

Each encoder provides:
- Channel A
- Channel B

Used for:
- speed measurement
- future odometry
- trajectory correction

GPIO allocation:

| Encoder | Raspberry Pi GPIO |
|---|---|
| Left Motor Encoder A | GPIO 23 |
| Left Motor Encoder B | GPIO 24 |
| Right Motor Encoder A | GPIO 25 |
| Right Motor Encoder B | GPIO 26 |

Encoder feedback can be enabled progressively.

Version 1 can operate without closed-loop motor control.

# Head Articulation System
The turtle head uses two servos to control movement.

Components:
- 2 x MG90S servo

The two degrees of freedom are:
- Pan: left/right rotation
- Tilt: up/down movement

---
## Pan Servo

Function:
- left/right head rotation

Connection:
| Signal | Raspberry Pi GPIO |
|---|---|
| PWM | GPIO 17 |

---

## Tilt Servo
Function:
- up/down head movement

Connection:
| Signal | Raspberry Pi GPIO |
|---|---|
| PWM | GPIO 27 |

Software: servo.py

---
# Audio System

## Speaker
Components:
- MAX98357A Class-D amplifier
- Speaker

Interface:
- I2S

GPIO allocation:
| Signal | Raspberry Pi GPIO |
|---|---|
| BCLK | GPIO 18 |
| LRCLK | GPIO 19 |
| DIN | GPIO 21 |

Software: audio.py

Functions:
- turtle voice
- sound effects
- notifications
- feedback sounds

---
# Lighting System
Spy Turtle uses two independent lighting systems.
- Shell lighting
- Status indicator

---
## Shell RGB LEDs
Component:
- WS2812B individually addressable RGB LED strip

Purpose:
- shell illumination
- animations
- effects

Connection:
| Signal | Connection |
|---|---|
| Data | GPIO 22 |
| Power | 5V |
| Ground | GND |

Software: leds.py

Functions:
- color effects
- brightness control
- animations
- robot states

A level shifter may be added if communication reliability requires it.

---

## Status RGB LED

Component:
- RGB status LED

Purpose:
Provide quick robot state indication:

Examples:
- startup
- connected
- battery status
- error state
- charging state

Connection:
Controlled through GPIO.

Final GPIO assignment will be validated during assembly.
---
# Raspberry Pi GPIO Allocation

Current GPIO allocation target:

| GPIO | Function |
|---|---|
| GPIO 2 | I2C SDA |
| GPIO 3 | I2C SCL |
| GPIO 4 | TB6612 STBY optional |
| GPIO 5 | Motor A direction |
| GPIO 6 | Motor A direction |
| GPIO 8 | TFT CS |
| GPIO 9 | SPI MISO |
| GPIO 10 | SPI MOSI |
| GPIO 11 | SPI Clock |
| GPIO 12 | Motor PWM A |
| GPIO 13 | Motor PWM B |
| GPIO 16 | Motor B direction |
| GPIO 17 | Head Pan Servo |
| GPIO 18 | I2S BCLK |
| GPIO 19 | I2S LRCLK |
| GPIO 20 | Motor B direction |
| GPIO 21 | I2S DIN |
| GPIO 22 | WS2812 LEDs |
| GPIO 23 | Left Encoder A |
| GPIO 24 | Left Encoder B |
| GPIO 25 | Right Encoder A |
| GPIO 26 | Right Encoder B |
| GPIO 27 | Head Tilt Servo |

Unused GPIOs remain available for future extensions.

---

# Power Distribution
The UPS HAT powers the complete robot.

Power domains:

## Raspberry Pi Domain
Powered by:
- Waveshare UPS HAT

Devices:
- Raspberry Pi 5
- Camera
- OLED displays
- TFT display logic
- Audio interface
- Sensors

---

## Motor Domain

Powered by:
- Battery system

Devices:
- TB6612FNG motor driver
- JGA25-370 motors

The motor power ground and Raspberry Pi ground must be common.
---

# Cable Management

Project rules:
- Use GPIO breakout board whenever possible.
- Prefer Dupont connectors.
- Avoid soldering whenever practical.
- Keep cables short and organized.
- Secure wiring using zip ties.
- Leave enough slack for maintenance.
- Keep wiring modular.

---

# Assembly Order
Recommended assembly sequence:
1. Assemble chassis.
2. Install motors.
3. Install wheels.
4. Install servos.
5. Mount Raspberry Pi.
6. Mount UPS HAT.
7. Install GPIO breakout board.
8. Connect camera.
9. Connect OLED displays.
10. Connect TFT display.
11. Connect motor driver.
12. Connect encoder signals.
13. Connect servos.
14. Connect speaker.
15. Connect LEDs.
16. Verify wiring.
17. Install batteries.
18. First power-on.

---
# First Boot Checklist
## Raspberry Pi
- [ ] Raspberry Pi OS boots successfully
- [ ] SSH available
- [ ] Network connection works

---

## UPS
- [ ] Battery detected
- [ ] Charging works
- [ ] Battery monitoring works

---

## Camera
- [ ] Camera detected
- [ ] Live stream available

---

## Displays
- [ ] Left OLED detected
- [ ] Right OLED detected
- [ ] TFT detected
- [ ] Shell display works

---

## Mobility
- [ ] Forward movement
- [ ] Backward movement
- [ ] Left turn
- [ ] Right turn
- [ ] Encoder reading

---

## Head
- [ ] Pan servo works
- [ ] Tilt servo works

---

## LEDs
- [ ] Shell LEDs power on
- [ ] Animations work
- [ ] Status LED works

---

## Audio
- [ ] Speaker detected
- [ ] Sound playback works

---

# Troubleshooting

## I2C Devices Not Detected

Check:
- SDA connection
- SCL connection
- Power
- I2C addresses

---

## Camera Not Detected

Check:
- CSI cable orientation
- Camera enabled in Raspberry Pi OS

---

## Motors Do Not Move

Check:
- Motor power
- Ground connection
- TB6612 STBY
- PWM signals
- Motor wiring

---

## Servo Problems

Check:
- 5V power supply
- Ground connection
- PWM GPIO assignment

---

## LEDs Do Not Respond

Check:
- Data GPIO
- 5V supply
- Ground
- Level shifter if required

---

# Hardware Design Decisions
| Decision | Reason |
|---|---|
| Raspberry Pi 5 | Enough computing power for vision and AI |
| Waveshare UPS HAT | Integrated power management |
| 21700 batteries | Higher capacity |
| GPIO breakout board | Easier wiring and maintenance |
| TB6612FNG | Efficient dual motor control |
| ST7796U TFT | Large color shell display |
| SSD1306 OLED | Simple animated eyes |
| WS2812B LEDs | Flexible RGB lighting |
| Dupont connectors | Modular maintenance |
| Minimal soldering | Easier assembly and repair |
| Simulation-first software | Hardware independent development |

---

# Version
Current hardware target:
Spy Turtle Version 1.0
This document represents the official hardware reference for the project.