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

# Raspberry Pi 40-pin Header

| Component | Pin | # | # | Pin | Component |
|---|---|---:|---:|---|---|
| 3.3V logic | 3.3V | 1 | 2 | 5V | Reserved |
| I2C SDA: UPS + OLED eyes | GPIO2 | 3 | 4 | 5V | ST7796 backlight |
| I2C SCL: UPS + OLED eyes | GPIO3 | 5 | 6 | GND | Common ground |
| WS2812B data | GPIO4 | 7 | 8 | GPIO14 | Available / UART TX |
| GND | GND | 9 | 10 | GPIO15 | Available / UART RX |
| Pan servo | GPIO17 | 11 | 12 | GPIO18 | MAX98357A BCLK (planned) |
| Tilt servo | GPIO27 | 13 | 14 | GND | Common ground |
| Available | GPIO22 | 15 | 16 | GPIO23 | Future encoder |
| 3.3V | 3.3V | 17 | 18 | GPIO24 | ST7796 RESET |
| ST7796 MOSI | GPIO10 | 19 | 20 | GND | Common ground |
| ST7796 MISO | GPIO9 | 21 | 22 | GPIO25 | ST7796 DC |
| ST7796 SCLK | GPIO11 | 23 | 24 | GPIO8 | ST7796 CS |
| GND | GND | 25 | 26 | GPIO7 | Available / SPI CE1 |
| Reserved ID_SD | GPIO0 | 27 | 28 | GPIO1 | Reserved ID_SC |
| TB6612 STBY | GPIO5 | 29 | 30 | GND | Common ground |
| TB6612 AIN1 | GPIO6 | 31 | 32 | GPIO12 | TB6612 PWMA |
| TB6612 AIN2 | GPIO13 | 33 | 34 | GND | Common ground |
| MAX98357A LRCLK (planned) | GPIO19 | 35 | 36 | GPIO16 | TB6612 BIN1 |
| TB6612 PWMB | GPIO26 | 37 | 38 | GPIO20 | TB6612 BIN2 |
| GND | GND | 39 | 40 | GPIO21 | MAX98357A DIN (planned) |

# 5V Power Rack

The rack is powered from a USB cable connected to the UPS USB 5V output. Only the cable's +5V and GND conductors are used.

| Rack rail | Source | Connected components | Status |
|---|---|---|---|
| +5V | UPS USB 5V output | TB6612 VM | Connected |
| +5V | UPS USB 5V output | Pan servo | Connected |
| +5V | UPS USB 5V output | Tilt servo | Connected |
| +5V | UPS USB 5V output | ST7796 backlight | Connected |
| +5V | UPS USB 5V output | WS2812B strip | Connected/planned final routing |
| +5V | UPS USB 5V output | MAX98357A VIN | Planned, replacement amplifier pending |
| GND | UPS USB GND | TB6612, servos, ST7796, LEDs, future amplifier | Common ground |

Important:
- TB6612 `VCC` uses Raspberry Pi 3.3V logic.
- TB6612 `VM` uses the external 5V rack.
- Raspberry Pi, UPS, rack and all peripherals must share a common ground.

# I2C Devices

| Address | Device |
|---|---|
| 0x2D | Waveshare UPS HAT |
| 0x3C | Left OLED eye |
| 0x3D | Right OLED eye |

---

# Hardware Overview

Spy Turtle is built around a Raspberry Pi 5.

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

## Power System
| Component | Quantity |
|---|---:|
| Waveshare UPS HAT | 1 |
| Panasonic NCR18650B 18650 Li-Ion batteries, 3350 mAh | 4 |
| USB-C Panel Mount | 1 |
| Inline Fuse Holder | 1 |
| 5A Fuse | 1 |
| 5V/GND terminal rack fed from UPS USB output | 1 |

---

# Vision System

## Camera
Component: Raspberry Pi Camera Module 3  
Connection: CSI interface directly connected to Raspberry Pi 5  
Power: Supplied by Raspberry Pi  
Software: `camera.py`

# Display System

## OLED Eyes
- I2C SDA: GPIO2
- I2C SCL: GPIO3
- Left: 0x3C
- Right: 0x3D

## ST7796 Shell Display
- MOSI: GPIO10
- MISO: GPIO9
- SCLK: GPIO11
- CS: GPIO8
- DC: GPIO25
- RESET: GPIO24
- Backlight: 5V rack
- SPI0 device 0

# Mobility System

## TB6612FNG
| Signal | GPIO |
|---|---|
| STBY | GPIO5 |
| PWMA | GPIO12 |
| AIN1 | GPIO6 |
| AIN2 | GPIO13 |
| PWMB | GPIO26 |
| BIN1 | GPIO16 |
| BIN2 | GPIO20 |

Power:
- `VCC` → Raspberry Pi 3.3V
- `VM` → 5V rack
- `GND` → common ground

Motors:
- Channel A: AO1/AO2
- Channel B: BO1/BO2
- Motor wires: red and white
- Encoder wires remain disconnected for now

# Head Articulation System
- Pan servo signal: GPIO17
- Tilt servo signal: GPIO27
- Servo power: 5V rack
- Servo ground: common ground

# Audio System
Status: planned; replacement MAX98357A board pending.

Final allocation:
- BCLK: GPIO18
- LRCLK: GPIO19
- DIN: GPIO21
- VIN: 5V rack
- GND: common ground

# Lighting System

## WS2812B Shell LEDs
- Data: GPIO4, physical pin 7
- Power: 5V rack
- Ground: common ground
- Device: `/dev/leds0`

Raspberry Pi 5 overlay:

```ini
dtoverlay=ws2812-pio,gpio=4,num_leds=32,brightness=255
```

The move from GPIO18 to GPIO4 removes the conflict with the planned MAX98357A I2S BCLK.

# Assembly and Validation Notes
- Camera validated.
- UPS detected at 0x2D.
- OLED eyes detected at 0x3C and 0x3D.
- Servos validated.
- ST7796 display validated.
- TB6612 and both motors validated through the final API/frontend.
- WS2812B validated previously on GPIO18; must be revalidated after moving DATA to GPIO4.
- Audio installation pending replacement amplifier.
- Encoders are not connected yet.
