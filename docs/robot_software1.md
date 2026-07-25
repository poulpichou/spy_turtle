# Spy Turtle - Robot Software Architecture

## Purpose

This document describes the software architecture of Spy Turtle.

The goal is to provide a clean separation between:

* robot logic
* hardware drivers
* simulation drivers
* API control
* future Raspberry Pi implementation

The software must run identically in:

* simulation mode on a development computer
* hardware mode on the Raspberry Pi

The robot behavior must never depend on the underlying hardware implementation.

---

# Architecture Overview

Spy Turtle follows this architecture:

```
Mobile Frontend
        |
        |
     REST API
        |
        |
  Robot Actions Layer
        |
        |
      Robot
        |
        |
      Brain
        |
        |
  Hardware Abstraction Layer
        |
        |
 Simulation / Real Hardware
```

---

# Main Principle

The robot software must not directly access hardware.

Example:

Wrong:

```python
GPIO.output(pin, True)
```

Correct:

```python
robot.leds.on()
```

The hardware implementation decides how the action is performed.

---

# Project Structure

```
robot/
|
├── api/
│   ├── app.py
│   └── actions.py
|
├── brain/
│   ├── brain.py
│   ├── idle.py
│   └── planner.py
|
├── factory/
│   └── robot_factory.py
|
├── hardware/
│   ├── motor.py
│   ├── leds.py
│   ├── camera.py
│   ├── battery.py
│   ├── speaker.py
│   └── servo.py
|
├── simulation/
│   ├── fake_motor.py
│   ├── fake_leds.py
│   ├── fake_camera.py
│   ├── fake_battery.py
│   ├── fake_speaker.py
│   ├── fake_servo.py
│   └── fake_face.py
|
├── system/
│   ├── robot.py
│   ├── runtime.py
│   └── state.py
|
└── startup/
    └── main.py
```

---

# RobotFactory

`RobotFactory` is the only place where robot components are created.

Example:

```python
RobotFactory(simulation=True)
```

creates:

```
FakeMotor
FakeLEDController
FakeCamera
FakeBattery
FakeSpeaker
FakeServo
FakeFace
```

Later:

```python
RobotFactory(simulation=False)
```

will create:

```
GPIO Motor
WS2812 PIO LED Controller
Raspberry Pi Camera
UPS Battery Controller
Software audio player
PWM Servo Controller
OLED Face
```

The rest of the software remains unchanged.

---

# Robot Object

The Robot object contains all physical components.

Current structure:

```python
Robot(
    motors,
    face,
    leds,
    camera,
    battery,
    speaker,
    servo
)
```

The Robot also contains:

* current state
* Brain controller

---

# Brain System

The Brain handles autonomous behavior.

Current responsibilities:

* idle behaviors
* future autonomous actions
* priorities

Examples:

```
Idle
 |
 +-- blink
 +-- look around
 +-- yawn
```

The Brain must never directly control hardware.

Correct:

```python
self.robot.face.look_left()
```

Incorrect:

```python
GPIO.write(...)
```

---

# Hardware Abstraction Layer

Every hardware component has two implementations:

```
Interface
   |
   +-- Simulation
   |
   +-- Real Hardware
```

The interface remains identical.

---

# Motors

Purpose:

Control robot movement.

Current API:

```python
forward()
backward()
turn_left()
turn_right()
stop()
```

Simulation:

```
FakeMotor
```

Future hardware:

```
TB6612FNG driver
+
JGA25-370 motors with encoders
```

---

# LEDs

Purpose:

Shell lighting and status indication.

Current implementation:

```
FakeLEDController
```

Functions:

```python
rainbow()
breathing(color)
static(color)
off()
```

Hardware implementation:

```
WS2812B addressable LEDs
Raspberry Pi 5 ws2812-pio overlay
/dev/leds0 byte stream
```

---

# Camera

Purpose:

Provide video stream and photos.

Current implementation:

```
FakeCamera
```

Functions:

```python
start()
stop()
get_frame()
```

Future hardware:

```
Raspberry Pi Camera Module 3
```

---

# Face Display

Purpose:

Display turtle emotions.

Current implementation:

```
FakeFace
```

Examples:

```python
blink()
set_expression("sleepy")
look_left()
look_right()
```

Future hardware:

```
OLED display
```

---

# Battery

Purpose:

Provide battery information.

Current implementation:

```
FakeBattery
```

Functions:

```python
get_level()
is_charging()
```

Future hardware:

```
Waveshare UPS HAT
```

---

# Speaker

Purpose:

Play turtle sounds and voice.

Current implementation:

```
FakeSpeaker
```

Functions:

```python
play(text)
stop()
set_volume(volume)
```

Current status:

```
Audio assets and software playback are supported.
The MAX98357A amplifier was removed from the current V1 hardware plan.
```

---

# Camera Servo System

The camera uses two servo axes.

Axis:

```
Pan  : left / right
Tilt : up / down
```

Current implementation:

```
FakeServo
```

Functions:

```python
look_left()
look_right()
look_up()
look_down()
center()
```

Future hardware:

```
2x PWM servo motors
```

---

