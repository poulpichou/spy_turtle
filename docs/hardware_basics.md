# Hardware & Programming Basics

A practical introduction to electronics, communication protocols, computer hardware, networks and programming concepts.

The goal of this document is to understand the basic concepts behind modern embedded systems, robotics, IoT devices and computers.

---

# 1. Electronics Fundamentals

Electronics is based on controlling electrical signals to process information or create physical actions.

## 1.1 Voltage, Current and Power

**Voltage (V)** is the electrical potential difference that pushes electrons through a circuit.
**Current (A)** is the amount of electrical flow through a component.
**Power (W)** represents the energy consumed by a device.

Formula:

```text
Power = Voltage × Current

P(W) = V(V) × I(A)
```

Example:

```text
5V × 2A = 10W
```

A power source must provide:

* The correct voltage.
* Enough current for all connected components.

## 1.2 Digital and Analog Signals

Electronic systems communicate using electrical signals.

### Analog Signals

An analog signal is continuous and can take any value inside a range.

Examples:

* Microphone signals.
* Temperature sensors.
* Traditional audio signals.

Example:

```text
0V → 1.2V → 2.7V → 3.3V
```

### Digital Signals

A digital signal uses discrete values.

Most electronic systems use:

```text
LOW  = 0V
HIGH = 3.3V or 5V
```

Digital signals are easier for computers to process because they are less sensitive to noise.

## 1.3 GPIO - General Purpose Input/Output

GPIO pins are programmable electrical connections available on many computers and microcontrollers.

A GPIO can work as an input or an output.

### Input

The processor reads information from the outside world.

Examples:

* Buttons.
* Sensors.
* Switches.

```text
Sensor → GPIO → Processor
```

### Output

The processor controls an external device.

Examples:

* LEDs.
* Relays.
* Motor control signals.

```text
Processor → GPIO → Device
```

GPIO pins usually operate at 3.3V or 5V logic levels.

Connecting an incorrect voltage can permanently damage hardware.

---

# 2. Communication

Electronic components need communication protocols to exchange information.

A communication protocol defines:

* How data is formatted.
* How devices synchronize.
* How information is transmitted.

## 2.1 Communication Concepts

### Serial Communication

Serial communication sends data one bit at a time through a communication channel.

```text
10110010

↓

1 → 0 → 1 → 1 → 0 → 0 → 1 → 0
```

Advantages:

* Requires few wires.
* Simple hardware.
* Works well over distances.

Examples:

* UART.
* SPI.
* I2C.

### Parallel Communication

Parallel communication sends multiple bits simultaneously using several wires.

```text
Bit 1 ─────────
Bit 2 ─────────
Bit 3 ─────────
Bit 4 ─────────
```

Advantages:

* Can be very fast.

Disadvantages:

* Requires many wires.
* Synchronization becomes difficult.

### Synchronous Communication

A synchronous protocol uses a shared clock signal.

One device generates timing pulses so all devices know when to read data.

```text
Clock:
_|-|_|-|_|-|_

Data:
__--___--__--
```

Examples:

* SPI.
* I2C.
* I2S.

### Asynchronous Communication

An asynchronous protocol does not use a shared clock.

Both devices agree beforehand on communication parameters, especially speed.

Example:

* UART.

### Bus

A bus is a shared communication pathway connecting several electronic devices.

A bus can transport:

* Data.
* Clock signals.
* Addresses.
* Control information.

```text
              CPU
               |
       ----------------
       |       |      |
     OLED   Sensor  Memory
```

## 2.2 Communication Protocols

### I2C - Inter-Integrated Circuit

I2C is a synchronous serial communication protocol designed for connecting multiple low-speed devices.

It uses only two wires:

```text
SDA = Data
SCL = Clock
```

Characteristics:

* Multi-master.
* Multi-slave.
* Devices have unique addresses.
* Multiple devices can share the same bus.

Applications:

* OLED displays.
* LCD displays.
* Sensors.
* Real-time clocks.

```text
          CPU
           |
        SDA/SCL
           |
   ----------------
   |       |      |
 OLED  Sensor  Clock
```

### SPI - Serial Peripheral Interface

SPI is a fast synchronous serial protocol using a master/slave architecture.

```text
MOSI → Master Out Slave In
MISO → Master In Slave Out
SCLK → Clock
CS   → Chip Select
```

Advantages:

* Very fast.
* Simple protocol.
* Good for short distances.

Applications:

* SD cards.
* LCD screens.
* Flash memory.
* EEPROM.
* ADC converters.
* DAC converters.

### UART - Universal Asynchronous Receiver Transmitter

UART is an asynchronous serial communication protocol.

```text
Device A          Device B

TX  ------------> RX
RX  <------------ TX
GND ------------ GND
```

Communication speed is defined by the baud rate.

Applications:

* GPS modules.
* Bluetooth modules.
* Debug consoles.
* Communication between processors.

### I2S - Inter-IC Sound

I2S is a communication protocol dedicated to digital audio.

Important:

**I2S has nothing to do with I2C.**

It transports digital audio data between components such as processors, amplifiers and DACs.

Applications:

* Digital microphones.
* Audio amplifiers.
* Speakers.
* DAC audio boards.

```text
Processor
    |
   I2S
    |
Audio amplifier
    |
 Speaker
```

### PCM - Pulse Code Modulation

PCM is the method used to represent analog audio as digital data.

```text
Analog sound
      ↓
Sampling
      ↓
Digital values
      ↓
Storage or transmission
```

Example:

```text
Analog:
~~~~~~~ sound wave ~~~~~~~

Digital samples:
120
145
167
190
155
```

PCM is commonly used in digital audio systems and I2S communication.

---

# 3. Hardware

Hardware is the physical layer where software interacts with electronic components.

## 3.1 Computing Hardware

### Microcontrollers

A microcontroller is a small computer designed for direct hardware control.

Examples:

* Arduino.
* ESP32.
* STM32.

Characteristics:

* Very low power consumption.
* Direct access to pins.
* Usually dedicated to one task.

Applications:

* Sensors.
* Small robots.
* Embedded systems.

### Single Board Computers (SBC)

A Single Board Computer is a complete computer integrated on one board.

Example:

* Raspberry Pi.

Characteristics:

* Runs an operating system.
* Supports networking.
* Runs multiple applications.

Applications:

* Robotics.
* Cameras.
* AI.
* Servers.

## 3.2 Hardware Extensions

### HAT - Hardware Attached on Top

A HAT is an expansion board designed to connect directly onto another board.

Examples:

* Power management boards.
* Motor controllers.
* Sensor boards.
* Display boards.
* Audio boards.

Advantages:

* Cleaner wiring.
* Standardized connections.
* Easier assembly.

```text
Raspberry Pi

      |
      |
     HAT

      |
Extra hardware
```

### Power Supplies

A power supply provides stable electrical energy.

Important parameters:

**Voltage**

* Must match component requirements.

**Current**

* Must be sufficient for all connected devices.

**Voltage Regulation**

* Converts unstable power sources into stable voltages.

```text
Battery
   |
Voltage regulator
   |
Electronic system
```

### Cooling

Electronic components generate heat.

Too much heat can cause:

* Reduced performance.
* Instability.
* Hardware damage.

Passive cooling:

* Heat sinks.
* Metal surfaces.

Active cooling:

* Fans.
* Temperature-controlled systems.

## 3.3 Hardware Components

### LEDs

Light Emitting Diodes convert electrical energy into light.

Applications:

* Status indicators.
* Lighting.
* Displays.

### Displays

Displays convert digital information into visual output.

Examples:

* OLED.
* LCD.
* E-paper.

Communication methods:

* I2C.
* SPI.
* HDMI.

### Motors

Motors convert electrical energy into mechanical movement.

Examples:

* DC motors.
* Servo motors.
* Stepper motors.

They usually require a motor driver because processors cannot directly provide enough current.

### Sensors

Sensors measure physical information.

Examples:

* Temperature.
* Distance.
* Light.
* Motion.
* Pressure.

They often communicate using:

* I2C.
* SPI.
* UART.

### Speakers and Audio Components

Speakers convert electrical signals into sound.

```text
Processor
    |
Digital audio signal
    |
Amplifier
    |
Speaker
```

---

# 4. Networks

Networks allow computers and electronic devices to exchange information.

A network connects devices using:

* Wired connections (Ethernet, fiber).
* Wireless connections (WiFi, Bluetooth, cellular).

## 4.1 Network Fundamentals

### Client and Server

A server provides a service.

A client requests information or services.

Example:

```text
Phone (Client)

      |
      | Request
      ↓

Robot (Server)

      |
      | Response
      ↓

Phone receives data
```

### Local Area Network (LAN)

A LAN connects devices inside a limited area.

```text
        Router

    /      |      \

 Phone  Laptop  Robot
```

### Internet

The Internet is a network of interconnected networks.

```text
Device
  |
Router
  |
Internet
  |
Remote Server
```

## 4.2 Network Protocols

### IP - Internet Protocol

IP provides addressing and routing.

Example:

```text
192.168.1.25
```

### TCP

TCP provides reliable communication.

Used by:

* Websites.
* SSH.
* File transfers.

### UDP

UDP provides faster communication with no delivery guarantee.

Used by:

* Video streaming.
* Games.
* Real-time applications.

### HTTP / HTTPS

HTTP is used for web communication.

HTTPS adds encryption.

Applications:

* Websites.
* Web applications.
* APIs.

### WebSocket

WebSocket enables continuous two-way communication.

Used for:

* Live dashboards.
* Robot control.
* Real-time data.

## 4.3 IP Addresses and Ports

An IP address identifies a machine.

A port identifies a service.

Example:

```text
IP: 192.168.1.50

Port 22  → SSH
Port 80  → HTTP
Port 443 → HTTPS
```

Communication uses:

```text
IP Address + Port
```

Example:

```text
192.168.1.50:22
```

## 4.4 Authentication and Security

Authentication:
"Who are you?"

Authorization:
"What are you allowed to do?"

### Password Authentication

```text
Username
+
Password
```

### Public Key Authentication

Uses:

* Private key: secret, kept by the user.
* Public key: shared with servers.

```text
Private Key
     |
Creates proof
     |
Server verifies with Public Key
```

## 4.5 SSH - Secure Shell

SSH allows secure remote access to another computer.

Uses:

* Server administration.
* Raspberry Pi control.
* Remote debugging.

```text
Laptop

   SSH connection

        ↓

Raspberry Pi
```

SSH key authentication:

```text
Laptop

Private Key

      |
 SSH Authentication

      |

Raspberry Pi

Public Key
authorized_keys
```

Advantages:

* More secure.
* No password required.
* Common in professional environments.

## 4.6 Network Security Basics

### Encryption

Transforms readable information into protected data.

### Firewall

Controls allowed network connections.

### Least Privilege

A system should only have the permissions it actually needs.

---

# 5. Programming

Programming creates instructions that control hardware and process information.

## 5.1 Programming Fundamentals

### Program

A program is a sequence of instructions executed by a processor.

```text
Read sensor
     ↓
Process information
     ↓
Make decision
     ↓
Control hardware
     ↓
Repeat
```

### Variables

Store information.

Example:

```python
temperature = 25
```

### Functions

Reusable blocks of instructions.

Example:

```python
def move_forward():
    start_motor()
```

### Loops

Repeat actions.

Example:

```python
while True:
    read_sensor()
    update_display()
```

### Libraries

Pre-written code providing additional functionality.

Example:

```python
import camera_library
```

## 5.2 How Python Runs on Hardware

Python is a high-level programming language.

The code passes through several layers before controlling hardware.

```text
Python Code
     |
Python Interpreter
     |
Bytecode
     |
Python Virtual Machine
     |
Operating System
     |
Hardware Drivers
     |
Electronic Component
```

### Python Interpreter

Reads Python instructions and executes them.

The most common implementation is CPython.

### Bytecode

Intermediate representation generated from Python code.

Not directly understood by the CPU.

### Python Virtual Machine

Executes Python bytecode.

### Operating System

Manages:

* Memory.
* Processes.
* Files.
* Hardware access.

### Hardware Drivers

Translate software requests into hardware commands.

Example:

```text
Python
 |
GPIO Library
 |
Driver
 |
Electrical Pin
 |
LED ON
```

## 5.3 High-Level vs Low-Level Programming

```text
High Level
-----------
Python
C++
C
Assembly
Machine Code
-----------
Low Level
```

High-level languages:

* Easier to write.
* Faster development.
* More portable.

Low-level languages:

* More control.
* Higher performance.
* More complexity.

---

# Final Overview

A complete hardware/software system follows this chain:

```text
User
 |
Application
 |
Programming Language
 |
Operating System
 |
Driver
 |
Communication Protocol
 |
Electronic Component
 |
Physical Action
```

Example:

```text
Phone App
    |
   WiFi
    |
Python Program
    |
GPIO / I2C / SPI
    |
Motor Driver
    |
Motor
    |
Robot moves
```
