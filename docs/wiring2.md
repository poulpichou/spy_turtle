# Troubleshooting

## I2C Devices Not Detected
Check:
- SDA on GPIO2
- SCL on GPIO3
- 3.3V power
- common ground
- addresses 0x2D, 0x3C and 0x3D

## Camera Not Detected
Check:
- CSI cable orientation
- camera connector seating
- `rpicam-hello`

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
- 5V rack
- common ground
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
The replacement MAX98357A is not installed yet.

Once installed, check:
- BCLK GPIO18
- LRCLK GPIO19
- DIN GPIO21
- 5V rack
- common ground
- ALSA device detection

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

| Decision | Reason |
|---|---|
| Raspberry Pi 5 | Vision, control and future AI |
| Waveshare UPS HAT | Battery power and monitoring |
| UPS USB output to 5V rack | High-current peripherals avoid Raspberry Pi GPIO 5V distribution |
| TB6612FNG | Efficient dual motor control |
| GPIO4 for WS2812B | Avoids conflict with MAX98357A BCLK on GPIO18 |
| GPIO18/19/21 for MAX98357A | Standard I2S allocation |
| ST7796U TFT | Large shell display |
| Two addressed OLED eyes | Independent I2C control |
| Shared common ground | Required signal reference across all power domains |
| Simulation-first software | Hardware-independent development |

# Current Hardware Target
Spy Turtle Version 1.0

This document follows `docs/wiring1.md` and completes the official hardware reference.
