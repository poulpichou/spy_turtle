# Wiring

## Table of contents

- [Wiring](#wiring)
  - [Table of contents](#table-of-contents)
  - [Purpose](#purpose)
- [Raspberry Pi 40-pin Header](#raspberry-pi-40-pin-header)
- [5V Power Rack](#5v-power-rack)
- [I2C Distribution Rack](#i2c-distribution-rack)
- [I2C Devices](#i2c-devices)
- [Hardware Overview](#hardware-overview)
- [Final Bill Of Materials](#final-bill-of-materials)
  - [Main Computer](#main-computer)
  - [Power System](#power-system)
- [Vision System](#vision-system)
  - [Camera](#camera)
  - [MLX90640 Thermal Camera](#mlx90640-thermal-camera)
- [Display System](#display-system)
  - [OLED Eyes](#oled-eyes)
  - [ST7796 Shell Display](#st7796-shell-display)
- [Mobility System](#mobility-system)
  - [TB6612FNG](#tb6612fng)
    - [Motor Wire Identification](#motor-wire-identification)
    - [Motor Encoders](#motor-encoders)
- [Head Articulation System](#head-articulation-system)
- [Audio System](#audio-system)
  - [MAX98357A I2S Amplifier](#max98357a-i2s-amplifier)
  - [USB Microphone](#usb-microphone)
- [Lighting System](#lighting-system)
  - [WS2812B Shell LEDs](#ws2812b-shell-leds)
- [Assembly and Validation Notes](#assembly-and-validation-notes)
- [Troubleshooting](#troubleshooting)
  - [I2C Distribution Rack](#i2c-distribution-rack-1)
- [I2C Devices Not Detected](#i2c-devices-not-detected)
  - [Camera Not Detected](#camera-not-detected)
  - [Thermal Camera Not Detected](#thermal-camera-not-detected)
  - [Motors Do Not Move](#motors-do-not-move)
  - [Servo Problems](#servo-problems)
  - [LEDs Do Not Respond After GPIO Move](#leds-do-not-respond-after-gpio-move)
  - [Audio Does Not Work](#audio-does-not-work)
- [Raspberry Pi Configuration Change](#raspberry-pi-configuration-change)
- [Hardware Design Decisions](#hardware-design-decisions)
- [Current Hardware Target](#current-hardware-target)

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

| Component                 | Pin    |  # |  # | Pin    | Component                |
| ------------------------- | ------ | -: | -: | ------ | ------------------------ |
| 3.3V logic / TB6612 VCC  | 3.3V   |  1 |  2 | 5V     | 5V (Power rack)          |
| I2C SDA: UPS + OLED eyes + MLX90640 | GPIO2 (I2C rack) |  3 |  4 | 5V (Power rack) | ST7796 backlight / peripherals |
| I2C SCL: UPS + OLED eyes + MLX90640 | GPIO3 (I2C rack) |  5 |  6 | GND (Power rack) | Common ground            |
| WS2812B data              | GPIO4  |  7 |  8 | GPIO14 | Available / UART TX      |
| GND (Power rack)          | GND    |  9 | 10 | GPIO15 | Available / UART RX      |
| Pan servo                 | GPIO17 | 11 | 12 | GPIO18 | MAX98357A BCLK           |
| Tilt servo                | GPIO27 | 13 | 14 | GND (Power rack) | Common ground            |
| Future left encoder A     | GPIO22 | 15 | 16 | GPIO23 | Future left encoder B    |
| 3.3V                      | 3.3V   | 17 | 18 | GPIO24 | ST7796 RESET             |
| ST7796 MOSI               | GPIO10 | 19 | 20 | GND (Power rack) | Common ground            |
| ST7796 MISO               | GPIO9  | 21 | 22 | GPIO25 | ST7796 DC                |
| ST7796 SCLK               | GPIO11 | 23 | 24 | GPIO8  | ST7796 CS                |
| GND (Power rack)          | GND    | 25 | 26 | GPIO7  | Available / SPI CE1      |
| Reserved ID\_SD           | GPIO0  | 27 | 28 | GPIO1  | Reserved ID\_SC          |
| TB6612 STBY               | GPIO5  | 29 | 30 | GND (Power rack) | Common ground            |
| TB6612 AIN1               | GPIO6  | 31 | 32 | GPIO12 | TB6612 PWMA              |
| TB6612 AIN2               | GPIO13 | 33 | 34 | GND (Power rack) | Common ground            |
| MAX98357A LRCLK           | GPIO19 | 35 | 36 | GPIO16 | TB6612 BIN1              |
| TB6612 PWMB               | GPIO26 | 37 | 38 | GPIO20 | TB6612 BIN2              |
| GND (Power rack)          | GND    | 39 | 40 | GPIO21 | MAX98357A DIN            |

# 5V Power Rack

The rack is powered from a USB cable connected to the UPS USB 5V output. Only the cable's +5V and GND conductors are used.

| Rack rail | Source            | Connected components                           | Status                                 |
| --------- | ----------------- | ---------------------------------------------- | -------------------------------------- |
| +5V       | UPS USB 5V output | TB6612 VM                                      | Connected                              |
| +5V       | UPS USB 5V output | Pan servo                                      | Connected                              |
| +5V       | UPS USB 5V output | Tilt servo                                     | Connected                              |
| +5V       | UPS USB 5V output | ST7796 backlight                               | Connected                              |
| +5V       | UPS USB 5V output | MLX90640 thermal camera                        | Connected                              |
| +5V       | UPS USB 5V output | WS2812B strip                                  | Connected/planned final routing        |
| +5V       | UPS USB 5V output | MAX98357A VIN                                  | Connected / testing                    |
| GND       | UPS USB GND       | TB6612, servos, ST7796, MLX90640, LEDs, MAX98357A | Common ground                       |

Important:

- TB6612 `VCC` uses Raspberry Pi 3.3V logic.
- TB6612 `VM` uses the external 5V rack.
- Raspberry Pi, UPS, rack and all peripherals must share a common ground.
- The Power rack is the primary 5V/GND distribution point for peripherals.
- The rack only distributes the UPS 5V and GND rails; it does not regulate or convert voltage.
- High-current peripherals should use the rack rather than Raspberry Pi 5V header pins.
- Total current draw must remain within the UPS output and wiring capabilities.

# I2C Distribution Rack

GPIO2 (SDA) and GPIO3 (SCL) are distributed through a dedicated rack with multiple connection points.

```text
GPIO2 / SDA
    |
    +--- SDA rack
         +--- UPS HAT
         +--- Left OLED
         +--- Right OLED
         +--- MLX90640

GPIO3 / SCL
    |
    +--- SCL rack
         +--- UPS HAT
         +--- Left OLED
         +--- Right OLED
         +--- MLX90640
```

The rack is only a physical distribution point. All devices remain on the same Raspberry Pi I2C bus and are differentiated by their I2C addresses.

# I2C Devices

| Address | Device            |
| ------- | ----------------- |
| 0x2D    | Waveshare UPS HAT |
| 0x33    | MLX90640 Thermal Camera |
| 0x3C    | Left OLED eye     |
| 0x3D    | Right OLED eye    |

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

| Component             | Quantity |
| --------------------- | -------: |
| Raspberry Pi 5        |        1 |
| 64GB microSD A2       |        1 |
| GeeekPi Active Cooler |        1 |

## Power System

| Component                                            | Quantity |
| ---------------------------------------------------- | -------: |
| Waveshare UPS HAT                                    |        1 |
| Panasonic NCR18650B 18650 Li-Ion batteries, 3350 mAh |        4 |
| USB-C Panel Mount                                    |        1 |
| Inline Fuse Holder                                   |        1 |
| 5A Fuse                                              |        1 |
| 5V/GND terminal rack fed from UPS USB output         |        1 |
| SDA/SCL I2C distribution rack                        |        1 |

---

# Vision System

## Camera

Component: Raspberry Pi Camera Module 3
Connection: CSI interface directly connected to Raspberry Pi 5
Power: Supplied by Raspberry Pi
Software: `camera.py`

## MLX90640 Thermal Camera

Component: MLX90640 thermal sensor  
Resolution: 32×24  
Interface: I2C  
Address: `0x33`  
Software: `thermal_camera.py`

Wire mapping:

| Wire colour | Function | Connection |
| ----------- | -------- | ---------- |
| White | SDA | GPIO2 via I2C rack |
| Green | SCL | GPIO3 via I2C rack |
| Black | GND | GND via Power rack |
| Red | VCC | 5V via Power rack |

Quick reference:

```text
White -> SDA
Green -> SCL
Black -> GND
Red   -> VCC
```

Image rotation can be configured in `settings.py`:

```python
THERMAL_ROTATION=0
```

Allowed values: `0`, `90`, `180`, `270`.

The thermal camera has been validated on address `0x33`. Thermal acquisition runs asynchronously so I2C frame reads do not block the API or robot controls.

# Display System

## OLED Eyes

- I2C SDA: GPIO2 via I2C rack
- I2C SCL: GPIO3 via I2C rack
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

| Signal | GPIO   |
| ------ | ------ |
| STBY   | GPIO5  |
| PWMA   | GPIO12 |
| AIN1   | GPIO6  |
| AIN2   | GPIO13 |
| PWMB   | GPIO26 |
| BIN1   | GPIO16 |
| BIN2   | GPIO20 |

Power:

- `VCC` → Raspberry Pi 3.3V
- `VM` → 5V rack
- `GND` → common ground

Motors:

- Channel A: AO1/AO2
- Channel B: BO1/BO2
- Motor wires: red and white
- Encoder wires remain disconnected for now

### Motor Wire Identification

Each motor has six wires: white, blue, green, yellow, black and red.

The DC motor pair was identified experimentally with the multimeter. The two motor wires are the two extreme wires:

```text
Red + White = DC motor
```

Current motor-driver output mapping:

```text
Left motor
AO1 -> Red
AO2 -> White

Right motor
BO1 -> Red
BO2 -> White
```

The motors are mounted in mirror orientation. Direction correction is handled in software using `MOTOR_LEFT_INVERTED` and `MOTOR_RIGHT_INVERTED`, so the physical motor wiring does not need to be swapped.

The remaining blue, green, yellow and black wires belong to the Hall encoder system. Their exact VCC/GND/A/B colour mapping has not yet been physically validated and must not be guessed from colour alone.

### Motor Encoders

Encoder wiring is currently optional and disabled in software.

Reserved GPIO allocation:

| Encoder | A | B |
| ------- | --- | --- |
| Left | GPIO22 | GPIO23 |
| Right | GPIO14 | GPIO15 |

Notes:

- GPIO14/GPIO15 are also UART TX/RX.
- Encoder output voltage must be confirmed before connection to Raspberry Pi GPIO.
- The motors operate normally without encoder wiring.

# Head Articulation System

- Pan servo signal: GPIO17
- Tilt servo signal: GPIO27
- Servo power: 5V rack
- Servo ground: common ground

Servo wire colours:

| Wire colour | Function | Connection |
| ----------- | -------- | ---------- |
| Brown | GND | GND Power rack |
| Red | +5V | 5V Power rack |
| Yellow / Orange | PWM signal | GPIO17 or GPIO27 |

Quick reference:

```text
Pan servo
Brown  -> GND Power rack
Red    -> 5V Power rack
Yellow -> GPIO17

Tilt servo
Brown  -> GND Power rack
Red    -> 5V Power rack
Yellow -> GPIO27
```

# Audio System

## MAX98357A I2S Amplifier

Final allocation:

- BCLK: GPIO18
- LRCLK: GPIO19
- DIN: GPIO21
- VIN: 5V Power rack
- GND: GND Power rack / common ground

Full wiring:

| MAX98357A | Connection |
| ---------- | ---------- |
| VIN | 5V Power rack |
| GND | GND Power rack |
| BCLK | GPIO18 |
| LRC / LRCLK / WS | GPIO19 |
| DIN | GPIO21 |
| SPK+ | Speaker + |
| SPK- | Speaker - |
| GAIN | Not connected |
| SD | Not connected |

The speaker must be connected directly between `SPK+` and `SPK-`. Neither speaker terminal should be connected to GND because the MAX98357A uses a bridge-tied output.

## USB Microphone

The microphone has an integrated USB audio interface and connects directly to a Raspberry Pi USB port. No GPIO connection is required.

Detection:

```bash
arecord -l
```

# Lighting System

## WS2812B Shell LEDs

- Data: GPIO4, physical pin 7
- Power: 5V rack
- Ground: common ground
- Device: `/dev/leds0`
Colors of wires
```
Red   -> 5V Power rack
Green -> GPIO4
White -> GND Power rack
```

Raspberry Pi 5 overlay:

```ini
dtoverlay=ws2812-pio,gpio=4,num_leds=32,brightness=255
```


The move from GPIO18 to GPIO4 removes the conflict with the MAX98357A I2S BCLK.

# Assembly and Validation Notes

- Camera validated.
- UPS detected at 0x2D.
- MLX90640 thermal camera detected at 0x33 and validated.
- OLED eyes detected at 0x3C and 0x3D.
- Servos validated.
- ST7796 display validated.
- TB6612 and both motors validated through the final API/frontend.
- WS2812B configured on GPIO4 as `/dev/leds0`.
- Replacement MAX98357A amplifiers received; GPIO18/19/21 wiring defined and amplifier available for validation.
- Encoders are not connected yet.
- Red/white motor wires identified experimentally as the DC motor pair.
- USB microphone connected and detected as a USB audio device.
- 5V/GND Power rack installed for peripheral power distribution.
- SDA/SCL I2C rack installed for shared I2C distribution.

# Troubleshooting

## I2C Distribution Rack

GPIO2 (SDA) and GPIO3 (SCL) are distributed through a dedicated rack with multiple connection points.

```text
GPIO2 / SDA
    |
    +--- SDA rack
         +--- UPS HAT
         +--- Left OLED
         +--- Right OLED
         +--- MLX90640

GPIO3 / SCL
    |
    +--- SCL rack
         +--- UPS HAT
         +--- Left OLED
         +--- Right OLED
         +--- MLX90640
```

The rack is only a physical distribution point. All devices remain on the same Raspberry Pi I2C bus and are differentiated by their I2C addresses.

# I2C Devices Not Detected

Check:

- SDA on GPIO2
- SCL on GPIO3
- 3.3V power
- common ground
- addresses 0x2D, 0x33, 0x3C and 0x3D

## Camera Not Detected

Check:

- CSI cable orientation
- camera connector seating
- `rpicam-hello`

## Thermal Camera Not Detected

Check:

- White → SDA / GPIO2 I2C rack
- Green → SCL / GPIO3 I2C rack
- Black → GND Power rack
- Red → 5V Power rack

Then run:

```bash
i2cdetect -y 1
```

Expected thermal-camera address: `0x33`.

API status:

```bash
curl -s http://localhost:8000/thermal/status
```

## Motors Do Not Move

Check:

- 5V rack output
- TB6612 VM and VCC
- common ground
- STBY GPIO5
- motor signal GPIO allocation
- red/white motor wires
- that Spy Turtle is not already reserving GPIOs during standalone diagnostics

## Servo Problems

Check:

- Brown wire → GND Power rack
- Red wire → 5V Power rack
- Yellow/Orange wire → PWM
- pan GPIO17
- tilt GPIO27

## LEDs Do Not Respond After GPIO Move

Check physical wiring:

- DATA moved from GPIO18 / physical pin 12
- DATA connected to GPIO4 / physical pin 7
- 5V and GND unchanged

Check overlay:

```bash
grep ws2812 /boot/firmware/config.txt
```

Expected:

```ini
dtoverlay=ws2812-pio,gpio=4,num_leds=32,brightness=255
```

Check kernel initialization:

```bash
dmesg | grep -i ws2812
```

Expected device:

- `/dev/leds0`

Then check permissions:

```bash
ls -l /dev/leds0
```

## Audio Does Not Work

Check:

- BCLK GPIO18
- LRCLK GPIO19
- DIN GPIO21
- VIN on 5V Power rack
- GND on common Power rack
- speaker connected only between SPK+ and SPK-
- ALSA device detection

Useful commands:

```bash
aplay -l
speaker-test -c2
arecord -l
```

# Raspberry Pi Configuration Change

The repository includes:

```text
scripts/configure_led_gpio4.sh
```

Run once on the Raspberry Pi after pulling the update:

```bash
chmod +x scripts/configure_led_gpio4.sh
sudo ./scripts/configure_led_gpio4.sh
sudo reboot
```

The script:

- backs up `/boot/firmware/config.txt`
- replaces an existing `ws2812-pio` GPIO assignment with GPIO4
- adds the correct overlay if none exists

# Hardware Design Decisions

| Decision                   | Reason                                                           |
| -------------------------- | ---------------------------------------------------------------- |
| Raspberry Pi 5             | Vision, control and future AI                                    |
| Waveshare UPS HAT          | Battery power and monitoring                                     |
| UPS USB output to 5V rack  | High-current peripherals avoid Raspberry Pi GPIO 5V distribution |
| Dedicated I2C distribution rack | Clean shared SDA/SCL distribution for UPS, OLEDs and MLX90640 |
| TB6612FNG                  | Efficient dual motor control                                     |
| Red/white motor wires      | Experimentally identified DC motor pair                          |
| Optional motor encoders    | Robot remains operational before encoder wiring is completed     |
| GPIO4 for WS2812B          | Avoids conflict with MAX98357A BCLK on GPIO18                    |
| GPIO18/19/21 for MAX98357A | Standard I2S allocation                                          |
| MLX90640 at 0x33           | Thermal vision over the existing shared I2C bus                  |
| USB microphone             | Audio input without additional GPIO allocation                  |
| ST7796U TFT                | Large shell display                                              |
| Two addressed OLED eyes    | Independent I2C control                                          |
| Shared common ground       | Required signal reference across all power domains               |
| Simulation-first software  | Hardware-independent development                                 |

# Current Hardware Target

Spy Turtle Version 1.0

Current hardware includes:

- Raspberry Pi 5
- Waveshare UPS HAT
- 4× Panasonic NCR18650B batteries
- UPS-fed 5V/GND Power rack
- SDA/SCL I2C distribution rack
- Raspberry Pi Camera Module 3
- MLX90640 thermal camera
- two OLED eyes
- ST7796 shell display
- TB6612FNG motor driver
- two JGA25-370 motors
- optional Hall encoders
- two MG90S servos
- WS2812B shell LEDs
- MAX98357A I2S amplifier
- 4Ω 3W speaker
- USB microphone

This document follows `docs/wiring1.md` and completes the official hardware reference.
