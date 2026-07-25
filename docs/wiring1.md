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
| Panasonic NCR18650B 18650 Li-Ion batteries, 3350 mAh | 4 |
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
- 1.3 inch OLED (final eye target)
- 128x64 resolution
- SH1106 driver

Earlier 0.96 inch SSD1306 hardware was used successfully for initial I2C display tests.
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
| DC / LCD_RS | GPIO 25 |
| RESET | GPIO 24 |
| Backlight | 5V |

Software: ST7796 display driver and shell UI modules. The driver uses SPI plus `lgpio` for control pins. On the current Raspberry Pi OS installation the GPIO header is exposed through `gpiochip0`; do not hard-code the obsolete `gpiochip4`.

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
Audio files are supported by the software asset catalog, including WAV and MP3 assets. The previously planned MAX98357A I2S amplifier was removed from the current V1 wiring, so GPIO 18, 19 and 21 are no longer reserved for that amplifier. A final physical audio output path will be selected and documented later.

---

# Lighting System
Spy Turtle uses two independent lighting systems.
- Shell lighting
- Status indicator

---
## Shell RGB LEDs
Component: WS2812B individually addressable RGB LED strip.

Purpose:
- shell illumination
- animations and directional effects
- emotion and shell-mode feedback

Connection:
| Signal | Connection |
|---|---|
| Data | GPIO 18 |
| Power | 5V |
| Ground | Common GND |

Raspberry Pi 5 configuration:

```ini
dtoverlay=ws2812-pio,gpio=18,num_leds=32,brightness=255
```

The overlay exposes `/dev/leds0`. The Python backend writes raw pixel bytes directly to that device and does not use `rpi_ws281x`. `/dev/leds0` must remain writable by the runtime user, normally through a persistent udev rule. A level shifter remains optional if the data signal proves unreliable.

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
| GPIO 18 | WS2812B data through ws2812-pio |
| GPIO 19 | Available after MAX98357A removal |
| GPIO 20 | Motor B direction |
| GPIO 21 | Available after MAX98357A removal |
| GPIO 22 | Available / future assignment |
| GPIO 23 | Left Encoder A |
| GPIO 24 | TFT RESET; encoder allocation must be revised |
| GPIO 25 | TFT DC / LCD_RS; encoder allocation must be revised |
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

# Current Hardware Validation Notes
Validated on the Raspberry Pi 5:
- Camera Module 3 detected as IMX708 and operational with `rpicam` tools.
- UPS HAT visible on I2C address `0x2D`.
- OLED test display visible on I2C address `0x3C`.
- MG90S servos physically moved and are now controlled through smooth target updates.
- ST7796U SPI display produced full-screen color and rendered shell UI content.
- WS2812B strip produced valid output through `/dev/leds0`.

Still requiring final hardware validation:
- Two-eye final SH1106 installation and address strategy.
- TB6612FNG motors and encoder pin allocation.
- Final audio output hardware.
- Complete power testing under simultaneous camera, displays, servos and LED load.

Important power note: the Raspberry Pi GPIO 5V rail can be convenient for bench tests, but servo and LED current peaks can cause voltage drops or sudden shutdowns. Final wiring must use a power path sized for simultaneous loads while keeping all grounds common.

---

