# Wiring

## Purpose

This document describes the complete hardware assembly of Spy Turtle.

It is the reference for:

* the Bill Of Materials (BOM)
* electrical wiring
* GPIO allocation
* power distribution
* mechanical assembly
* hardware configuration

Any hardware modification should be reflected in this document.

---

# Hardware Overview

```
                     +--------------------+
                     |   Raspberry Pi 5   |
                     +---------+----------+
                               |
                +--------------+--------------+
                |                             |
         Camera Module                 Breakout Board
                |                             |
      +---------+----------+---------+--------+
      |         |          |         |        |
   OLED L    OLED R    TB6612     Servo   MAX98357
                              |
                         DC Motors
```

The Raspberry Pi contains all software logic.

Every peripheral is connected either directly to the Raspberry Pi or through the GPIO breakout board.

---

# Final Bill Of Materials

## Main Computer

| Component | Quantity |
|------------|---------:|
| Raspberry Pi 5 | 1 |
| 64 GB microSD (A2) | 1 |

---

## Power

| Component | Quantity |
|------------|---------:|
| Waveshare UPS HAT (4-cell version) | 1 |
| Samsung 21700 Li-Ion cells | 4 |
| USB-C Panel Mount | 1 |
| Inline Fuse Holder | 1 |
| 5 A Automotive Fuse | 1 |

---

## Mobility

| Component | Quantity |
|------------|---------:|
| JGA25-370 DC Motor (6 V / 280 RPM) | 2 |
| Wheel Encoders | 2 |
| TB6612FNG Motor Driver | 1 |
| 2WD Chassis | 1 |

---

## Vision

| Component | Quantity |
|------------|---------:|
| Raspberry Pi Camera Module 3 | 1 |

---

## User Feedback

| Component | Quantity |
|------------|---------:|
| 0.96" OLED Display | 2 |
| WS2812 RGB LED Strip | 1 |
| MAX98357A I2S Amplifier | 1 |
| Speaker | 1 |

---

## Motion

| Component | Quantity |
|------------|---------:|
| MG90S Servo | 2 |

---

## Wiring

| Component | Quantity |
|------------|---------:|
| GPIO Breakout Board | 1 |
| Dupont Wires | 1 kit |
| Nylon Spacers | 1 kit |
| Zip Ties | 1 pack |

---

## Cooling

| Component | Quantity |
|------------|---------:|
| GeeekPi Active Cooler | 1 |

---

## Future Hardware

Not part of Version 1.

* Microphone
* IMU
* ToF sensor
* GPS
* Charging dock
* Environmental sensors

## Actual links
role	model	Where?
Brain	Raspberry Pi 5	amazon
Brain	microSD 64GB 	amazon
Power	Waveshare UPS HAT 2S ou 4S	https://www.amazon.de/-/en/Waveshare-UPS-HAT-Raspberry-Bi-Directional/dp/B0DBLMFX57/ref=sr_1_1?crid=77HVWKH9TXJV&dib=eyJ2IjoiMSJ9.RszjCpKxxzppFm-K5SSzrvGx-kQRNISWsHxnH_kMHlj_NntzzVRj10HX9jW9u4wb5wRVSVMKmtwcq1uc_kGnajQI32JNencTnJCm7VNZGiaJ7cGs3GbO_kr7wgggPFkH1wWYmxSd7cmY5sOiyT13kcCL5zuZLxdtgfIGsFPsUtShJC0L8PvaAtDLTtF6YGF5BwaihyJj0h-XsXwcb-PGngdZDmv39Ol9nU-IO_YV7Ys.U8DfBEBWhlPu7zdzaiz63IuChoV4iswKp3FHZrPzHSg&dib_tag=se&keywords=Waveshare+UPS+HAT&qid=1782936548&sprefix=waveshare+ups+hat%2Caps%2C111&sr=8-1
Power	18650 batteries (x4)	https://www.galaxus.ch/fr/s1/product/everactive-2x-18650-li-ion-panasonic-ncr18650bschachtel-2-pcs-18650-3350-mah-batteries-piles-35785435?offertype=marketplace&offerid=8534185&utm_source=google&utm_medium=cpc&utm_campaign=PMax:+PROD_CH_SSC_Cluster_NoData&campaignid=20979242056&adtype=pla&adgroupid=&adid=&dgCidg=Cj0KCQjw9ZLSBhCcARIsAEhGKgPYJNxUgEJkxltl_OJ17pRRgGsp28AcpeFdXNvypTxdAJ6RorkwufkaArpyEALw_wcB&gclsrc=aw.ds&gad_source=1&gad_campaignid=20975944958&gbraid=0AAAAADmCc4NKzh2keIvl3SDiaNZc9Ll2u&gclid=Cj0KCQjw9ZLSBhCcARIsAEhGKgPYJNxUgEJkxltl_OJ17pRRgGsp28AcpeFdXNvypTxdAJ6RorkwufkaArpyEALw_wcB
Power Alimentation	USB-C Panel Mount	https://www.amazon.de/-/en/gp/product/B0GDHZ3243/ref=sw_img_1?th=1
Motion	Moteurs DC avec encodeurs	https://www.amazon.fr/-/en/OMVUMMHOB-209BF99F/dp/B0GXVKH8LZ/ref=sr_1_1?crid=214OQRH42UCER&dib=eyJ2IjoiMSJ9.fSC16qD1eeQkbw6PVKX5BvwKZKp9rJsYzj8WKjAuOIGVosRd7445XJz_twKFHpN1rb2F8UTFlegl8rdaNWYt8TNQb8h5puWNwixIFe26WMlTusLJFQX4WWxw5tjeXBJ-ug4l9yUJpw8wqjN28nzY6E7c_pj0lDmPlrkhH3eLzCeD_M2iRcWG4aSL7tSCWXgX8h7ThJQcxiomuOu8t-beDvYmWjXU__C9a9ACJg1F-E55dybPhJS5nZGPndThLsFtxWUfOBPPdx94D2G9FSI-1e5jS3cGADg3R7teW6vukfg.eXV_9tBosaGm5noJeaFLqrBptkiddublEzGr4N86NcQ&dib_tag=se&keywords=JGA25-370%2BDC%2BReduction%2BHall%2BMotor%2Bwith%2BEncoder%2BSpeedometer%2C%2BStrong%2BTorque%2B(280rpm%2C%2B6V)&qid=1782933883&sprefix=%2Caps%2C696&sr=8-1&th=1
Motion	TB6612FNG motor driver	https://www.amazon.de/-/en/gp/product/B0CQCMPYXJ/ref=sw_img_1?smid=A3JF3T1CRN0KMB&psc=1
Wheel	2WD Chassis	https://www.amazon.de/-/en/HpLive-Chassis-Platform-Encoder-Battery/dp/B0DKJ5FHHN/ref=sr_1_5?crid=NBVY1A9SRNGF&dib=eyJ2IjoiMSJ9.SCBHbetDuUk17vHGHN5KptkVh2TitmTYXuVDZAzra1aBWWl47gOx5_-UJm_Id8e3038sjBLqF0-V0YnGnJWR4dLeVqIy83IIIsJLz2QOtWql_jVTx3oltwaHHs5sGtO_kaYhf2YUgDaGVCne_JkIm0yt83-e90sL7-poDio8x-WzSVpElzew6YrfTE5vAIScWAMbfeHY2mW78IXtKw5khACY9vOUZrWg7014blRRqbI0vKMKG6ft1bvZf74BFjdeyABPvZrpQjz37MuarK1EABmbkYqVDY6atMVmc6mCeDo.lLIAueaH4eM5P-nqVvRp-UgJJywehZKMMhcAYbTViOU&dib_tag=se&keywords=2WD+chassis&qid=1783022235&s=toys&sprefix=2wd+chassis%2Ctoys%2C89&sr=1-5
Camera	Raspberry Pi Camera Module 3	https://www.amazon.de/-/en/gp/product/B0BRY6MVXL/ref=ox_sc_act_title_9?smid=A1JDLVO3NW19TT&th=1
Wiring	Breakout board	https://www.amazon.de/Ulegqin/dp/B0GY84DYR4/ref=sr_1_14_sspa?crid=BQGDJHJUCC86&dib=eyJ2IjoiMSJ9.ZQ5OiS-jzaBbHh2V1bWJHk4jCyDk4s_1qsmWTO3xvxqLtHY4qNMKQaXz_PTezsDxDyFdjHgWJi5zuJ8gCJdYZB06WZCpYB3sF46PGY3QK9BoSbfNlyJUJU0B-y_a1_f0_uulNeqTNt-P3KCIqP3ICaHeQkAPTS8P3FCW7C_rzZjQSwBiVcLpqtIBdfWmQ96VaEoraWJvbuFJjcexbJfHkMuNtRzkW_KWnUDfl3XSWVbPZvWZzbQQ3iNSIU_dpoG_ikTVUF6c70nSIPHpLv5Zt83IQobuwwylyqiTqfGd2fo.Xl8jL3xWmNiDj6DwWL2h1hyNjnDe3EcIrqJWINkpwx0&dib_tag=se&keywords=breakout+board&qid=1783020774&sprefix=breakout+board%2Caps%2C139&sr=8-14-spons&aref=BHM4vlILbg&sp_csd=d2lkZ2V0TmFtZT1zcF9tdGY&psc=1
LED	WS2812 LED x60	https://www.amazon.de/LOAMLIN-WS2812B-Programmable-Individually-Addressable/dp/B0956C7KFR/ref=sr_1_2_sspa?crid=1WB7IFBYTM2EH&dib=eyJ2IjoiMSJ9.d6P5q8_ZIijEzWZabMfaSZIPRbjaOY0CURq2OdnKUE9_xki7__hBYvJWQqLeQjRzWRYC43CjaLCLTH0ByO-bmmnW3mUn8GT72j0D0vTprf534m-g6kl8cEFtiyzOBgITqhOBzGXWW-Cq4HQfcLlnOEL8cmLfcLViD0n1Qkol32N-mbaNWJ9Oqgms1tgL3Q261nNbbdupElhp8J-RgezBiwJxwK7a3g17kbhv442N_T6TlnJ76V7BA69F7svUJrmCO6ngUsIk_nyHbDRYV27GxusxQiaKvpEjDrblPVTQ6MQ.tXhvg0K6cu-d3fDps9pAzzl-WT_LctZUbeBpxZYeo3o&dib_tag=se&keywords=WS2812%2BLED&qid=1783020399&sprefix=ws2812%2Bled%2B%2Caps%2C111&sr=8-2-spons&aref=LnOLVcgHsp&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1
Audio	MAX98357A amplifier + speaker	https://www.amazon.de/-/en/gp/product/B0H14TPFMV/ref=sw_img_1?smid=A3IN3R0HFAWJY8&th=1
Servo	MG90S servo	https://www.amazon.de/-/en/gp/product/B0G7GKGJSY/ref=ox_sc_act_title_1?smid=A39HBTAU2IT6N7&th=1
Wiring	Fils Dupont	https://www.amazon.de/-/en/Elegoo-120pcs-Multicolored-Breadboard-arduino/dp/B01EV70C78/ref=sr_1_5?dib=eyJ2IjoiMSJ9.smLJPjX1ALmjpddoGBMqvghNBt_K2hK0zNukzj0OYx7VFnsSY-s1sQ6mto-FYThPjB5wcJhRCMYk9QNjVwHXu8dDIiHl40UKBStlMi8rqljzZgYNXFF9BRTDGFjXKKdAttV-7W3ZDJPKrr5YkT-1CVmkjZQSdjVE99WGi8xvxhzKdUsiWu6bMsjHQOGV68qH04PLINzjm8VOx4QcWUb2-xZmGTXwOUQJqRGxytFz1BRhokvRr-o6i-3tJC-v3SESyx_4VNWFdHFvb9EsKEg26B7Yp4yoJgmLC-w5-4VZ_Ds.gpm_luUluZ8IoV5oTo64wxhAKtoXIwEBDllGB1fF8vc&dib_tag=se&keywords=dupont%2Bjumper%2Bwires%2Bkit&qid=1782935148&sr=8-5&th=1
Wiring	Zip ties	https://www.amazon.de/-/en/gp/product/B08SNNSV12/ref=sw_img_1?smid=A3JWKAKR8XB7XF&psc=1
Cooler	GeeekPi Active Cooler for Raspberry Pi 5	https://www.amazon.de/-/en/gp/product/B0CNVDF2MC/ref=ox_sc_act_title_8?smid=A187Y4UVM6ZA0X&th=1
Screen	0.96' OLED Display Module I2C IIC 128x64 (x2)	https://www.amazon.de/-/en/gp/product/B0B7RPCZ4Z/ref=sw_img_1?smid=A187Y4UVM6ZA0X&psc=1


---

# Mechanical Layout

Planned physical arrangement.

```
 ______________________________

          Camera

      OLED      OLED

    Raspberry Pi 5

    Waveshare UPS

   Breakout Board

 Speaker       Servo

______________________________

     Motor     Motor

      Wheels
```

The exact position may evolve during assembly.

The objective is to keep wiring short and maintenance easy.

---

# GPIO Allocation

The exact GPIO allocation will be frozen during assembly.

| GPIO | Function |
|------|----------|
| GPIO 2 | I2C SDA |
| GPIO 3 | I2C SCL |
| GPIO 12 | Servo PWM |
| GPIO 18 | Motor PWM A |
| GPIO 19 | Motor PWM B |
| GPIO 20 | Motor Direction |
| GPIO 21 | Motor Direction |
| GPIO 23 | WS2812 LEDs (planned) |
| GPIO 40 | Audio I2S |

Unused GPIOs remain available for future extensions.

---

# Wiring

## Raspberry Pi

The Raspberry Pi is the central controller.

All software executes on the Raspberry Pi.

---

## UPS HAT

Connected directly on top of the Raspberry Pi.

Provides:

* battery charging
* battery protection
* uninterrupted power
* battery monitoring

Powered by:

* 4 × Samsung 21700 cells

---

## Camera

Connection:

CSI ribbon cable.

Power:

Directly from the Raspberry Pi.

Software:

camera.py

---

## OLED Displays

Connection:

I2C

Typical addresses:

```
0x3C
0x3D
```

Software modules:

* eyes.py
* mouth.py

---

## Motors

Connection:

TB6612FNG

Controlled by:

motors.py

Power:

UPS HAT

---

## Servos

Connection:

PWM GPIO

Controlled by:

servo.py

Power:

5 V supply

---

## LEDs

Connection:

Single GPIO data line.

Powered from:

5 V supply.

Controlled by:

leds.py

A level shifter may be added if required for reliable communication.

---

## Speaker

Connection:

MAX98357A

Interface:

I2S

Controlled by:

audio.py

---

# Power Distribution

```
21700 Batteries

        │

        ▼

Waveshare UPS HAT

        │

        ▼

 Raspberry Pi

        │

        ▼

GPIO Devices

 • OLED
 • Servo
 • LEDs
 • Audio
 • Motor Driver
```

The UPS powers the complete robot.

No external power distribution board is planned.

---

# Cable Management

The project follows a few simple rules.

* Use the GPIO breakout board whenever possible.
* Prefer Dupont connectors.
* Avoid soldering whenever practical.
* Keep cables as short as possible.
* Secure wiring using zip ties.
* Leave enough slack for maintenance.
* Keep wiring modular.

---

# Assembly Order

Recommended assembly sequence.

1. Assemble the chassis.
2. Install both motors.
3. Install the wheels.
4. Install the servos.
5. Mount the Raspberry Pi.
6. Mount the UPS HAT.
7. Install the breakout board.
8. Connect the camera.
9. Connect the OLED displays.
10. Connect the motor driver.
11. Connect the speaker.
12. Connect the LEDs.
13. Verify all wiring.
14. Install batteries.
15. First power-on.

---

# First Boot Checklist

## Raspberry Pi

☐ Boots successfully

☐ Raspberry Pi OS starts

☐ SSH available

---

## UPS

☐ Battery detected

☐ Charging works

☐ Battery level readable

---

## Camera

☐ Camera detected

☐ Live stream available

---

## OLED Displays

☐ Left display detected

☐ Right display detected

☐ Face displayed correctly

---

## Motors

☐ Forward

☐ Backward

☐ Left

☐ Right

☐ Stop

---

## Servo

☐ Left

☐ Right

☐ Center

---

## LEDs

☐ Power on

☐ Rainbow animation

☐ Brightness control

---

## Audio

☐ Speaker detected

☐ Startup sound plays

---

# Troubleshooting

## OLED not detected

Check:

* SDA
* SCL
* I2C address

Run:

```bash
i2cdetect -y 1
```

---

## Camera not detected

Run:

```bash
libcamera-hello
```

---

## Motors do not move

Check:

* VM power
* STBY pin
* PWM pins
* Motor wiring

---

## Servo jitters

Check:

* power supply
* grounding
* PWM configuration

---

## LEDs do not respond

Check:

* data GPIO
* power supply
* ground
* level shifter (if installed)

---

# Hardware Design Decisions

| Decision | Reason |
|----------|--------|
| Raspberry Pi 5 | Enough computing power for computer vision and AI |
| Waveshare UPS HAT | Integrated charging and battery monitoring |
| Samsung 21700 cells | Higher capacity than 18650 |
| GPIO Breakout Board | Cleaner wiring and easier maintenance |
| TB6612FNG | Efficient and compact motor driver |
| WS2812 LED Strip | Flexible enough to wrap around the shell |
| Dupont connectors | Easy maintenance and replacement |
| Minimal soldering | Faster assembly and easier repairs |
| Simulation-first software | Hardware can be developed independently from software |

---

# Version

Current hardware target:

**Spy Turtle Version 1.0**

This document represents the official hardware reference for the project.