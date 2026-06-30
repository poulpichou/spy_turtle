# 🔌 Spy Turtle — Wiring Manual

## 🎯 Overview

This document describes how to connect all electronic components of the Spy Turtle robot.

The system is based on:

- Raspberry Pi 5 (main controller)
- TB6612FNG motor driver
- Waveshare GPIO Expansion HAT
- Waveshare UPS HAT 2S (power supply)
- Optional peripherals (camera, LEDs, audio, display)

---

## ⚠️ Safety Notes

- Always disconnect power before wiring
- Double-check polarity (especially battery and motor power)
- Do not power motors directly from Raspberry Pi
- Use common GND between all modules

---

## 🧠 System Layout

            ┌──────────────────────┐
            │   Raspberry Pi 5     │
            └─────────┬────────────┘
                      │ GPIO
    ┌─────────────────┼─────────────────┐
    │                 │                 │

┌───────▼───────┐ ┌───────▼───────┐ ┌─────▼───────┐
│ TB6612 Driver │ │ GPIO HAT │ │ Camera CSI │
│ (Motors) │ │ (Expansion) │ │ Module 3 │
└───────┬───────┘ └───────┬───────┘ └─────────────┘
│ │
Motors L/R LEDs / Servo / Fan

            ↓
 ┌──────────────────────┐
 │ Waveshare UPS HAT 2S │
 │ (Battery + 5V rail)  │
 └──────────────────────┘

---

## 🚗 Motor Driver (TB6612FNG)

### Power

| TB6612 Pin | Connection |
|------------|-----------|
| VM         | Battery (7.4V / 2S) |
| VCC        | 3.3V (Raspberry Pi) |
| GND        | Common GND |

---

### Raspberry Pi GPIO Mapping

#### Left Motor

| TB6612 Pin | Raspberry Pi GPIO |
|------------|------------------|
| PWMA       | GPIO12 (PWM)     |
| AIN1       | GPIO23           |
| AIN2       | GPIO24           |

#### Right Motor

| TB6612 Pin | Raspberry Pi GPIO |
|------------|------------------|
| PWMB       | GPIO13 (PWM)     |
| BIN1       | GPIO27           |
| BIN2       | GPIO22           |

#### Standby

| TB6612 Pin | Raspberry Pi GPIO |
|------------|------------------|
| STBY       | GPIO17           |

---

## 🔋 Power System

### Waveshare UPS HAT 2S

- Battery: 2x 18650 (2S configuration)
- Output: stable 5V to Raspberry Pi
- Built-in charging via USB-C or DC input

### Power Flow


Battery → UPS HAT → Raspberry Pi 5 → GPIO → Modules
↓
Motors (via TB6612 VM)


---

## 🎥 Camera (future integration)

| Component | Connection |
|----------|-----------|
| Camera Module 3 | CSI ribbon cable |

- Connect directly to Raspberry Pi CSI port
- No GPIO required

---

## 💡 GPIO Expansion HAT

Used for easy prototyping:

- LEDs
- Servo motors
- Fan control
- OLED display (I2C/SPI)

No strict mapping yet (depends on future modules)

---

## 💡 Recommended Wiring Rules

- Always share **GND between all modules**
- Keep motor power (VM) separate from logic power (3.3V/5V)
- Use short wires for motor driver signals
- Avoid routing motor wires near camera ribbon cable

---

## 🧪 Testing Checklist

Before first run:

- [ ] Raspberry Pi boots from UPS HAT
- [ ] GPIO HAT is detected
- [ ] TB6612 has correct power (VM + VCC)
- [ ] Motors spin freely when tested
- [ ] No overheating on regulator
- [ ] Common ground confirmed

---

## 🚀 Future Expansion

This wiring layout supports:

- Encoders (odometry)
- Pan/tilt camera
- LIDAR sensor
- AI modules (voice, vision)