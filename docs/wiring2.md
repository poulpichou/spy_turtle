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
WN-BC4090  5st35a9ti1
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